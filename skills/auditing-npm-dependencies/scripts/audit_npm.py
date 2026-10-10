#!/usr/bin/env python3
"""auditing-npm-dependencies — wrap `npm audit --json` into canonical Findings.

Walks a Node.js project, runs `npm audit --json` in the target directory, parses
both the v1 (npm 6) and v2 (npm 7+) audit output shapes, and emits Findings via
lib/finding.py. Output formats (json/jsonl/markdown) and exit-code semantics are
shared with the rest of the penetration-tester v3 pack via lib/report.py.

The scanner deduplicates per-CVE across direct + transitive dependency paths,
classifies each finding as direct vs transitive (impacts remediation strategy),
and maps npm's severity vocabulary (info/low/moderate/high/critical) onto the
shared Severity enum.

Usage:
    python3 audit_npm.py PATH [--output FILE] [--format json|jsonl|markdown]
                              [--min-severity sev] [--include-dev] [--no-cache]
                              [--json-only]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# --- Make lib/ importable regardless of CWD ----------------------------------
_LIB_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_LIB_ROOT))

from lib.finding import Finding, Severity, ToolError  # noqa: E402
from lib import report  # noqa: E402


SKILL_ID = "auditing-npm-dependencies"
CATEGORY = "dependency-vulnerability"
CWE_DEFAULT = "CWE-1104"  # Use of unmaintained / vulnerable third-party component
NPM_LOCKFILES = ("package-lock.json", "npm-shrinkwrap.json")
FOREIGN_LOCKFILES = ("yarn.lock", "pnpm-lock.yaml")
# npm 6 marks an advisory with no patched release this way.
V1_NO_FIX = "<0.0.0"


# --- npm invocation ----------------------------------------------------------


def _npm_binary() -> str | None:
    """Resolve npm on PATH. On Windows this is `npm.cmd`, which `subprocess`
    only finds when given the resolved path.
    """
    return shutil.which("npm")


def _project_is_node(directory: Path) -> bool:
    """A directory is a node project if it has package.json at the root."""
    return (directory / "package.json").exists()


def _declared_dependencies(directory: Path) -> set[str]:
    """Names the root package.json declares itself (any dependency group)."""
    try:
        manifest = json.loads((directory / "package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot read package.json in {directory}: {exc}") from exc
    names: set[str] = set()
    for group in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        names.update((manifest.get(group) or {}).keys())
    return names


def _run_npm_audit(directory: Path, include_dev: bool, no_cache: bool) -> tuple[dict[str, Any], str]:
    """Run `npm audit --json` in directory, return (parsed_json, raw_stdout).

    Raises ToolError when npm did not produce an audit report: a failed audit
    must never read as a clean dependency tree.
    """
    npm = _npm_binary()
    if npm is None:
        raise ToolError("npm was not found on PATH; install Node.js to run this audit")
    cmd: list[str] = [npm, "audit", "--json"]
    if not include_dev:
        cmd.append("--omit=dev")
    if no_cache:
        # Revalidate cached registry data instead of trusting it.
        cmd.append("--prefer-online")
    try:
        proc = subprocess.run(  # noqa: S603 — npm is the audit tool
            cmd,
            cwd=str(directory),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolError("npm audit timed out after 180s") from exc
    except OSError as exc:
        raise ToolError(f"could not run npm: {exc}") from exc

    stdout = proc.stdout or ""
    # npm audit exits non-zero when vulns are found — that's expected; we
    # parse the JSON regardless.
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        reason = (proc.stderr or stdout).strip()[:500] or "no output"
        raise ToolError(
            f"npm audit returned non-JSON output: {reason}. "
            "A corrupt cache is a common cause: `npm cache clean --force` and retry."
        ) from exc
    if not isinstance(data, dict):
        raise ToolError("npm audit report has an unknown shape")
    if "error" in data:
        # Missing lockfile (ENOLOCK), registry outage, lockfile out of sync.
        err = data["error"] if isinstance(data["error"], dict) else {"summary": str(data["error"])}
        raise ToolError(f"npm audit failed: {err.get('code', '')} {err.get('summary', '')}".strip())
    return data, stdout


# --- npm v2 schema parser (npm 7+) -------------------------------------------


def _parse_v2(data: dict[str, Any], target_label: str, declared: set[str]) -> list[Finding]:
    """Parse npm 7+ audit output. Schema is `vulnerabilities.<pkg> → record`.

    npm reports one record per vulnerable package, with every advisory for it
    under `via`. A package is direct when the root package.json declares it,
    transitive otherwise.
    """
    findings: list[Finding] = []
    vulns: dict[str, Any] = data.get("vulnerabilities", {}) or {}

    for pkg_name, record in vulns.items():
        severity_str = str(record.get("severity", "info"))
        severity = Severity.from_npm_audit(severity_str)

        via = record.get("via", [])
        is_direct = pkg_name in declared
        source_label = "direct" if is_direct else "transitive"

        # Extract CVE / GHSA from any dict entries in `via`.
        cve_id: str | None = None
        ghsa_id: str | None = None
        title_summary: str | None = None
        urls: list[str] = []
        for item in via:
            if not isinstance(item, dict):
                continue
            raw_source = item.get("source")
            # npm audit v2 sometimes emits `source` as a list, sometimes as a
            # scalar (string advisory ID or integer advisory ID). Normalize.
            source_list: list[Any] = []
            if isinstance(raw_source, list):
                source_list = raw_source
            elif raw_source is not None:
                source_list = [raw_source]
            for src in source_list:
                if isinstance(src, str) and src.upper().startswith("CVE-"):
                    cve_id = cve_id or src
                if isinstance(src, str) and src.upper().startswith("GHSA-"):
                    ghsa_id = ghsa_id or src
            cve_id = cve_id or item.get("cve") or None
            # When source is itself a GHSA string, surface it as ghsa_id.
            source_str = raw_source if isinstance(raw_source, str) else None
            ghsa_id = ghsa_id or item.get("ghsa") or source_str or None
            title_summary = title_summary or item.get("title")
            url = item.get("url")
            if url:
                urls.append(url)

        affected_range = str(record.get("range", "unknown"))
        fix_available = record.get("fixAvailable", False)
        if isinstance(fix_available, dict):
            fix_version_str = f"{fix_available.get('name', pkg_name)}@{fix_available.get('version', '?')}"
        elif fix_available is True:
            fix_version_str = "non-breaking upgrade available (npm audit fix)"
        else:
            fix_version_str = "no fix available"

        title = title_summary or f"npm vulnerability in {pkg_name} ({severity_str})"

        detail_lines = [
            f"Affected package: {pkg_name}",
            f"Affected range: {affected_range}",
            f"Dependency relationship: {source_label}",
            f"npm severity: {severity_str}",
        ]
        if cve_id:
            detail_lines.append(f"CVE: {cve_id}")
        if ghsa_id:
            detail_lines.append(f"GHSA: {ghsa_id}")

        if is_direct:
            remediation = (
                f"1. Run `npm audit fix` in {target_label}.\n"
                f"2. If fix requires a semver-major bump, evaluate breaking changes "
                f"and decide whether to upgrade.\n"
                f"3. Commit the updated package-lock.json."
            )
        else:
            remediation = (
                f"1. Run `npm ls {pkg_name}` to identify which parent(s) pull in "
                f"the vulnerable version.\n"
                f"2. Check whether upgrading the parent picks up the fix.\n"
                f"3. If not, add a root-level `overrides` block for {pkg_name} "
                f"pinning to the fix version (requires npm 8.3+)."
            )

        if fix_version_str.startswith("no fix"):
            remediation += (
                "\n\nNO FIX AVAILABLE — subscribe to GHSA notifications and "
                "consider vendoring + patching or replacing the package."
            )

        evidence_items: list[tuple[str, Any]] = [
            ("package", pkg_name),
            ("range", affected_range),
            ("relationship", source_label),
            ("fix", fix_version_str),
        ]
        if cve_id:
            evidence_items.append(("cve", cve_id))
        if ghsa_id:
            evidence_items.append(("ghsa", ghsa_id))

        # Bump severity to HIGH if no fix and originally moderate+ — operator
        # has limited remediation surface.
        if fix_version_str.startswith("no fix") and severity.numeric >= 3:
            severity = max(severity, Severity.HIGH, key=lambda s: s.numeric)

        findings.append(
            Finding(
                skill_id=SKILL_ID,
                title=title,
                severity=severity,
                target=f"{target_label}::{pkg_name}",
                detail="\n".join(detail_lines),
                remediation=remediation,
                cve_id=cve_id,
                cwe_id=CWE_DEFAULT,
                references=tuple(urls or []),
                evidence=tuple(evidence_items),
            )
        )

    return findings


# --- npm v1 schema parser (npm 6) --------------------------------------------


def _parse_v1(data: dict[str, Any], target_label: str) -> list[Finding]:
    """Parse npm 6 audit output. Schema is `advisories.<id> → record`."""
    findings: list[Finding] = []
    advisories: dict[str, Any] = data.get("advisories", {}) or {}

    for adv_id, record in advisories.items():
        severity_str = str(record.get("severity", "info"))
        severity = Severity.from_npm_audit(severity_str)
        pkg_name = record.get("module_name", "<unknown>")
        affected_range = record.get("vulnerable_versions", "unknown")
        patched_versions = record.get("patched_versions", "")
        cves = record.get("cves") or []
        cve_id = cves[0] if cves else None
        title = record.get("title") or f"npm advisory {adv_id} in {pkg_name}"
        url = record.get("url", "")

        detail_lines = [
            f"Affected package: {pkg_name}",
            f"Affected versions: {affected_range}",
            f"npm severity: {severity_str}",
            f"Advisory ID: {adv_id}",
        ]
        if cve_id:
            detail_lines.append(f"CVE: {cve_id}")

        if str(patched_versions).strip() in ("", V1_NO_FIX):
            remediation = (
                "NO FIX AVAILABLE — subscribe to GHSA notifications and "
                "consider vendoring + patching or replacing the package."
            )
            if severity.numeric >= 3:
                severity = max(severity, Severity.HIGH, key=lambda s: s.numeric)
        else:
            remediation = (
                f"1. Upgrade {pkg_name} to a version matching `{patched_versions}`.\n"
                "2. Run `npm install` to refresh package-lock.json.\n"
                "3. Re-run audit to confirm the finding is resolved."
            )

        findings.append(
            Finding(
                skill_id=SKILL_ID,
                title=title,
                severity=severity,
                target=f"{target_label}::{pkg_name}",
                detail="\n".join(detail_lines),
                remediation=remediation,
                cve_id=cve_id,
                cwe_id=CWE_DEFAULT,
                references=(url,) if url else (),
                evidence=(
                    ("package", pkg_name),
                    ("affected", affected_range),
                    ("patched", patched_versions),
                    ("advisory_id", adv_id),
                ),
            )
        )

    return findings


# --- Operational helpers -----------------------------------------------------


def _info_finding(title: str, detail: str, target: str) -> Finding:
    return Finding(
        skill_id=SKILL_ID,
        title=title,
        severity=Severity.INFO,
        target=target,
        detail=detail,
        remediation="Operational issue; no security action required.",
        references=(),
        evidence=(),
    )


def audit_directory(directory: Path, include_dev: bool, no_cache: bool, json_only: bool) -> tuple[list[Finding], str]:
    """Run an audit, returning (findings, raw_stdout)."""
    if not _project_is_node(directory):
        raise ToolError(f"target is not a Node project: no package.json at {directory}")
    if not any((directory / name).exists() for name in NPM_LOCKFILES):
        foreign = [name for name in FOREIGN_LOCKFILES if (directory / name).exists()]
        hint = (
            f" Found {', '.join(foreign)}: use that package manager's own audit (`yarn npm audit`, `pnpm audit`)."
            if foreign
            else " Run `npm install --package-lock-only` first."
        )
        raise ToolError(f"no package-lock.json or npm-shrinkwrap.json in {directory}.{hint}")
    declared = _declared_dependencies(directory)

    data, raw = _run_npm_audit(directory, include_dev, no_cache)
    if json_only:
        sys.stdout.write(raw)
        return [], raw

    target_label = directory.name or str(directory)
    if "vulnerabilities" in data:
        findings = _parse_v2(data, target_label, declared)
    elif "advisories" in data:
        findings = _parse_v1(data, target_label)
    else:
        raise ToolError("npm audit report has neither `vulnerabilities` nor `advisories`")

    if not findings:
        findings = [
            _info_finding(
                "no npm vulnerabilities found",
                "npm audit reported a clean dependency tree.",
                str(directory),
            )
        ]
    return findings, raw


# --- CLI ---------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("path", help="Path to Node project root (contains package.json)")
    p.add_argument("--output", default=None, help="Write findings to FILE (default: stdout)")
    p.add_argument(
        "--format",
        default="markdown",
        choices=["json", "jsonl", "markdown"],
        help="Output format (default: markdown)",
    )
    p.add_argument(
        "--min-severity",
        default="info",
        choices=["info", "low", "medium", "high", "critical"],
        help="Filter out findings below this severity (default: info — emit all)",
    )
    p.add_argument(
        "--include-dev",
        action="store_true",
        help="Audit devDependencies too (default: prod only)",
    )
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="Pass --prefer-online to npm so cached registry data is revalidated (slower; fresher data)",
    )
    p.add_argument(
        "--json-only",
        action="store_true",
        help="Print raw npm audit --json and exit (debug)",
    )
    return p


def _filter_min_severity(findings: list[Finding], min_sev: str) -> list[Finding]:
    floor = Severity(min_sev).numeric
    return [f for f in findings if f.severity.numeric >= floor]


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    directory = Path(args.path).resolve()

    findings, _raw = audit_directory(
        directory,
        include_dev=args.include_dev,
        no_cache=args.no_cache,
        json_only=args.json_only,
    )
    if args.json_only:
        return 0

    findings = _filter_min_severity(findings, args.min_severity)
    report.emit(findings, args.output, args.format, scan_target=str(directory))
    return report.exit_code(findings)


if __name__ == "__main__":
    sys.exit(report.run(main))
