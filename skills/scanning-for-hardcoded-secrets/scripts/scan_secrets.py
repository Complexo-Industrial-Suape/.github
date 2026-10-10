#!/usr/bin/env python3
"""Static-analysis scan for hardcoded credentials in source trees.

Companion to skill `scanning-for-hardcoded-secrets`. Walks a directory
tree, reads each text file, applies the canonical credential regex
library, and emits findings with file path + line number + redacted
matched text.

Two detection modes layered:

1. Provider-specific regex (AWS AKIA, GitHub ghp_, Stripe sk_live_,
   Anthropic sk-ant-, OpenAI sk-proj-, Slack xox*, Google AIza, RSA
   private keys, etc.). These are CRITICAL because tools at the
   receiving end (AWS, GitHub Secret Scanning, vendor bots)
   auto-extract.

2. Entropy + context-based heuristics (high-Shannon-entropy string
   appearing in a `key:` / `token:` / `password=` field). HIGH or
   MEDIUM. Higher false-positive rate; requires human verification.

References:
    CWE-798 Use of Hard-coded Credentials
    CWE-321 Use of Hard-coded Cryptographic Key
    OWASP A07:2021 Identification and Authentication Failures
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib.finding import Finding, Severity, ToolError  # noqa: E402
from lib.report import emit, exit_code, run  # noqa: E402

SKILL_ID = "scanning-for-hardcoded-secrets"


# Provider-specific regex library.
# Each entry: (pattern_name, severity, regex, control)
PROVIDER_REGEXES = [
    ("AWS access key", Severity.CRITICAL, r"\b(AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}\b", "CWE-798"),
    ("GitHub personal access token", Severity.CRITICAL, r"\bghp_[A-Za-z0-9]{36,}\b", "CWE-798"),
    ("GitHub OAuth token", Severity.CRITICAL, r"\bgho_[A-Za-z0-9]{36,}\b", "CWE-798"),
    ("GitHub app installation token", Severity.CRITICAL, r"\bghs_[A-Za-z0-9]{36,}\b", "CWE-798"),
    ("GitHub user-to-server token", Severity.CRITICAL, r"\bghu_[A-Za-z0-9]{36,}\b", "CWE-798"),
    ("GitHub refresh token", Severity.CRITICAL, r"\bghr_[A-Za-z0-9]{36,}\b", "CWE-798"),
    ("Stripe live secret key", Severity.CRITICAL, r"\bsk_live_[A-Za-z0-9]{24,}\b", "CWE-798"),
    ("Stripe restricted key (live)", Severity.CRITICAL, r"\brk_live_[A-Za-z0-9]{24,}\b", "CWE-798"),
    ("Stripe test secret key", Severity.MEDIUM, r"\bsk_test_[A-Za-z0-9]{24,}\b", "CWE-798"),
    ("Anthropic API key", Severity.CRITICAL, r"\bsk-ant-(?:api|sid)\d+-[A-Za-z0-9_-]{20,}\b", "CWE-798"),
    ("OpenAI API key", Severity.CRITICAL, r"\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}\b", "CWE-798"),
    ("Slack bot token", Severity.CRITICAL, r"\bxoxb-[A-Za-z0-9-]{10,}\b", "CWE-798"),
    ("Slack user token", Severity.CRITICAL, r"\bxoxp-[A-Za-z0-9-]{10,}\b", "CWE-798"),
    ("Slack workspace token", Severity.CRITICAL, r"\bxoxa-[A-Za-z0-9-]{10,}\b", "CWE-798"),
    (
        "Slack webhook URL",
        Severity.HIGH,
        r"\bhttps://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24,}\b",
        "CWE-798",
    ),
    (
        "Discord bot token",
        Severity.CRITICAL,
        r"\b[MN][A-Za-z0-9_-]{23,28}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{27,}\b",
        "CWE-798",
    ),
    ("Google API key", Severity.HIGH, r"\bAIza[A-Za-z0-9_-]{35}\b", "CWE-798"),
    ("Google OAuth refresh token", Severity.HIGH, r"\b1//[A-Za-z0-9_-]{40,}\b", "CWE-798"),
    ("Twilio account SID", Severity.HIGH, r"\bAC[A-Za-z0-9]{32}\b", "CWE-798"),
    ("Twilio auth token", Severity.CRITICAL, r"\bSK[A-Za-z0-9]{32}\b", "CWE-798"),
    ("Mailgun API key", Severity.CRITICAL, r"\bkey-[a-f0-9]{32}\b", "CWE-798"),
    ("SendGrid API key", Severity.CRITICAL, r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b", "CWE-798"),
    ("Square access token", Severity.CRITICAL, r"\bsq0(?:atp|csp)-[A-Za-z0-9_-]{22,}\b", "CWE-798"),
    ("npm access token", Severity.CRITICAL, r"\bnpm_[A-Za-z0-9]{36,}\b", "CWE-798"),
    ("PyPI API token", Severity.CRITICAL, r"\bpypi-[A-Za-z0-9_-]{50,}\b", "CWE-798"),
    ("Cloudflare API token", Severity.CRITICAL, r"\b[A-Za-z0-9_-]{40}\b(?=.*cloudflare)", "CWE-798"),
    # Private keys — the regex marker strings below match secret-scanner
    # patterns by design; this is the detector library, not real keys.
    ("RSA private key", Severity.CRITICAL, "-" * 5 + "BEGIN RSA PRIVATE KEY" + "-" * 5, "CWE-321"),  # gitleaks:allow
    (
        "OpenSSH private key",
        Severity.CRITICAL,
        "-" * 5 + "BEGIN OPENSSH PRIVATE KEY" + "-" * 5,
        "CWE-321",
    ),  # gitleaks:allow
    ("EC private key", Severity.CRITICAL, "-" * 5 + "BEGIN EC PRIVATE KEY" + "-" * 5, "CWE-321"),  # gitleaks:allow
    ("DSA private key", Severity.CRITICAL, "-" * 5 + "BEGIN DSA PRIVATE KEY" + "-" * 5, "CWE-321"),  # gitleaks:allow
    (
        "PGP private key",
        Severity.CRITICAL,
        "-" * 5 + "BEGIN PGP PRIVATE KEY BLOCK" + "-" * 5,
        "CWE-321",
    ),  # gitleaks:allow
    (
        "Generic PEM private key",
        Severity.CRITICAL,
        "-" * 5 + "BEGIN PRIVATE KEY" + "-" * 5,
        "CWE-321",
    ),  # gitleaks:allow
]

# Context-based regex (field-name + value). Each entry:
# (pattern, label, severity, entropy_floor). An entropy_floor of None means
# "use the --entropy-threshold value". Patterns run in order and the first
# one to claim a value wins, so the specific fields come before the generic.
#
# The value must not be followed by `(`, `.` or `[`: that shape is a function
# call or attribute access, not a literal.
_VALUE_END = r"""(?![\w(.\[])"""
DEFAULT_ENTROPY_THRESHOLD = 3.5
PASSWORD_ENTROPY_FLOOR = 3.0
CONTEXT_PATTERNS = [
    (
        r"""(?P<key>aws_secret_access_key)[\s:=]+['"]?(?P<val>[A-Za-z0-9+/=_-]{16,})['"]?""" + _VALUE_END,
        "AWS secret access key",
        Severity.CRITICAL,
        None,
    ),
    (
        r"""(?P<key>(?:password|passwd|api[_-]?key|secret[_-]?key|"""
        r"""auth[_-]?token|access[_-]?token|jwt[_-]?secret|signing[_-]?secret|"""
        r"""client[_-]?secret|private[_-]?key|encryption[_-]?key))[\s:=]+['"]?"""
        r"""(?P<val>[A-Za-z0-9+/=_-]{16,})['"]?""" + _VALUE_END,
        "Credential-shaped value in known field",
        Severity.HIGH,
        None,
    ),
    (
        # A quoted password literal is a finding on its own; only obvious
        # dictionary-word values are filtered out by the lower floor.
        r"""(?P<key>password|passwd)\s*[:=]\s*['"](?P<val>[^'"\s]{8,})['"]""",
        "Password literal",
        Severity.HIGH,
        PASSWORD_ENTROPY_FLOOR,
    ),
    (
        r"""(?P<key>\b[A-Za-z0-9_-]*(?:key|token))\s*[:=]\s*['"]?(?P<val>[A-Za-z0-9+/=_-]{20,})['"]?""" + _VALUE_END,
        "High-entropy value in key/token field",
        Severity.MEDIUM,
        None,
    ),
]

# Placeholder-detection — these don't trigger a finding
PLACEHOLDER_MARKERS = (
    "<",
    ">",
    "EXAMPLE",
    "PLACEHOLDER",
    "YOUR_",
    "YOUR-",
    "XXXX",
    "XXX-",
    "TODO",
    "FIXME",
    "REDACTED",
    "REPLACEME",
    "REPLACE-ME",
    "REPLACE_ME",
    "CHANGEME",
    "FAKE",
    "DUMMY",
    "SAMPLE",
    "TEST_KEY_",
)

# Extensions / directories to skip
SKIP_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "target",
    ".cache",
    ".pnpm-store",
    ".venv",
    "venv",
    "__pycache__",
    ".astro",
    ".next",
    ".nuxt",
    "vendor",
}
TEXT_EXTS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".mjs",
    ".cjs",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".java",
    ".kt",
    ".scala",
    ".c",
    ".cpp",
    ".cc",
    ".h",
    ".hpp",
    ".cs",
    ".swift",
    ".m",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".md",
    ".rst",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".jsonc",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
    ".envrc",
    ".xml",
    ".html",
    ".vue",
    ".svelte",
    ".dockerfile",
    ".pem",
    ".key",
}
# Files that hold credentials by convention and have no telling extension.
SECRET_FILENAMES = {"dockerfile", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".npmrc", ".pypirc", ".netrc"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs"}


def is_candidate(path: Path) -> bool:
    name = path.name.lower()
    # `.env`, `.env.local`, `.env.production`: Path.suffix is empty for the first.
    return path.suffix.lower() in TEXT_EXTS or name in SECRET_FILENAMES or name.startswith(".env")


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    total = len(s)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def looks_like_placeholder(value: str) -> bool:
    upper = value.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


def redact(s: str, head: int = 4, tail: int = 4) -> str:
    if len(s) <= head + tail + 3:
        return "***"
    return f"{s[:head]}...{s[-tail:]}"


def should_skip_path(rel_path: Path, include_tests: bool, skip_dirs: set) -> bool:
    """Decide on the path relative to the scan root, never the absolute one:
    a repository checked out under `build/` or `test/` must still be scanned.
    """
    parts = set(rel_path.parts[:-1])
    if parts & skip_dirs:
        return True
    if not include_tests and parts & TEST_DIRS:
        return True
    return False


def scan_file(
    file_path: Path,
    repo_root: Path,
    include_provider: bool = True,
    include_context: bool = True,
    entropy_threshold: float = DEFAULT_ENTROPY_THRESHOLD,
) -> list[Finding]:
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return []
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, ValueError):
        return []

    try:
        rel = str(file_path.relative_to(repo_root))
    except ValueError:
        rel = str(file_path)
    return scan_text(text, rel, include_provider, include_context, entropy_threshold)


def scan_text(
    text: str,
    rel: str,
    include_provider: bool = True,
    include_context: bool = True,
    entropy_threshold: float = DEFAULT_ENTROPY_THRESHOLD,
) -> list[Finding]:
    """Apply the regex library to one blob of text labelled `rel`."""
    findings = []

    if include_provider:
        for name, sev, pattern, control in PROVIDER_REGEXES:
            for m in re.finditer(pattern, text):
                matched = m.group(0)
                if looks_like_placeholder(matched):
                    continue
                line_no = text[: m.start()].count("\n") + 1
                findings.append(
                    Finding(
                        skill_id=SKILL_ID,
                        title=f"{name} in {rel}:{line_no}",
                        severity=sev,
                        target=f"{rel}:{line_no}",
                        detail=(
                            f"File {rel} line {line_no} contains a string "
                            f"matching the {name} pattern. Matched value (redacted): "
                            f"`{redact(matched)}`. If this is a real credential it "
                            "is now in git history; rotate immediately and audit "
                            "logs for unauthorized use."
                        ),
                        remediation=(
                            f"Move {name} out of source. Set it in an environment "
                            "variable, secrets manager (AWS Secrets Manager, GCP "
                            "Secret Manager, HashiCorp Vault, Doppler), or "
                            "runtime-provisioned secret. See references/PLAYBOOK.md "
                            "for per-language patterns. Then rotate the credential."
                        ),
                        cwe_id=control,
                        affected_control="OWASP A07:2021",
                        evidence=(
                            ("file", rel),
                            ("line", line_no),
                            ("pattern", name),
                            ("redacted_match", redact(matched)),
                        ),
                    )
                )

    if include_context:
        claimed: set[int] = set()
        for pattern, label, sev, entropy_floor in CONTEXT_PATTERNS:
            floor = entropy_threshold if entropy_floor is None else entropy_floor
            for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                value = m.group("val")
                if m.start("val") in claimed:
                    continue
                if looks_like_placeholder(value):
                    continue
                # A literal with no digit is almost always an identifier.
                if entropy_floor is None and not any(ch.isdigit() for ch in value):
                    continue
                if shannon_entropy(value) < floor:
                    continue
                claimed.add(m.start("val"))
                line_no = text[: m.start()].count("\n") + 1
                key = m.group("key")
                findings.append(
                    Finding(
                        skill_id=SKILL_ID,
                        title=f"{label} in {key} field at {rel}:{line_no}",
                        severity=sev,
                        target=f"{rel}:{line_no}",
                        detail=(
                            f"File {rel} line {line_no} assigns a high-entropy "
                            f"value (Shannon entropy ≥ {floor}) to "
                            f"a {key} field. Redacted: `{redact(value)}`. "
                            "Likely a real credential."
                        ),
                        remediation=(
                            "Move the value out of source. Replace with environment-"
                            "variable lookup at startup. Rotate the credential."
                        ),
                        cwe_id="CWE-798",
                        affected_control="OWASP A07:2021",
                        evidence=(("file", rel), ("line", line_no), ("field", key), ("redacted_match", redact(value))),
                    )
                )

    return findings


def walk_repo(root: Path, include_tests: bool, extra_exclude: list[str]) -> list[Path]:
    out = []
    # Build exclude-match list
    exclude_patterns = [re.compile(re.escape(p).replace(r"\*", ".*")) for p in extra_exclude]
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if should_skip_path(rel, include_tests, SKIP_DIRS):
            continue
        if not is_candidate(p):
            continue
        if any(ep.search(rel.as_posix()) for ep in exclude_patterns):
            continue
        out.append(p)
    return out


def scan_git_history(
    root: Path, commits: int, include_provider: bool, entropy_threshold: float
) -> list[Finding]:
    """Scan the lines added by the last `commits` commits.

    A secret removed from the working tree is still in history; this is the
    only pass that sees it.
    """
    git = shutil.which("git")
    if git is None:
        raise ToolError("--git-history needs git on PATH")
    try:
        proc = subprocess.run(  # noqa: S603 — fixed argv, no shell
            [git, "-C", str(root), "log", "-p", "--no-color", "--unified=0", f"-n{commits}", "--format=commit %H"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=300,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolError("git log timed out after 300s") from exc
    if proc.returncode != 0:
        raise ToolError(f"git log failed: {proc.stderr.strip() or 'not a git repository'}")

    added: dict[tuple[str, str], list[str]] = {}
    commit = path = ""
    for line in proc.stdout.splitlines():
        if line.startswith("commit "):
            commit = line[7:19]
        elif line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else ""
        elif line.startswith("+") and path:
            added.setdefault((commit, path), []).append(line[1:])

    findings: list[Finding] = []
    for (sha, file_path), lines in added.items():
        if not is_candidate(Path(file_path)):
            continue
        findings.extend(
            scan_text(
                "\n".join(lines),
                f"git:{sha}:{file_path}",
                include_provider=include_provider,
                include_context=True,
                entropy_threshold=entropy_threshold,
            )
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hardcoded-secrets scanner")
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", default=None)
    parser.add_argument("--format", choices=("json", "jsonl", "markdown"), default="markdown")
    parser.add_argument("--min-severity", choices=("critical", "high", "medium", "low", "info"), default="info")
    parser.add_argument(
        "--include-tests", action="store_true", help="Include test directories in scan (default: excluded)"
    )
    parser.add_argument("--exclude", action="append", default=[], help="Skip files matching glob (repeatable)")
    parser.add_argument(
        "--entropy-only", action="store_true", help="Skip provider-regex pass; only emit entropy-based findings"
    )
    parser.add_argument(
        "--entropy-threshold",
        type=float,
        default=DEFAULT_ENTROPY_THRESHOLD,
        help=f"Minimum Shannon entropy for field-context findings (default: {DEFAULT_ENTROPY_THRESHOLD})",
    )
    parser.add_argument(
        "--git-history",
        type=int,
        default=0,
        metavar="N",
        help="Also scan the lines added by the last N commits (default: 0 = working tree only)",
    )
    args = parser.parse_args(argv)

    root = args.path.resolve()
    if not root.exists():
        raise ToolError(f"path does not exist: {root}")

    if root.is_file():
        files, base = [root], root.parent
    else:
        files, base = walk_repo(root, args.include_tests, args.exclude), root
    findings: list[Finding] = []
    for f in files:
        findings.extend(
            scan_file(
                f,
                base,
                include_provider=not args.entropy_only,
                include_context=True,
                entropy_threshold=args.entropy_threshold,
            )
        )
    if args.git_history > 0:
        findings.extend(
            scan_git_history(base, args.git_history, not args.entropy_only, args.entropy_threshold)
        )

    floor = Severity(args.min_severity)
    findings = [f for f in findings if f.severity.numeric >= floor.numeric]

    emit(findings, args.output, args.format, str(root))
    return exit_code(findings)


if __name__ == "__main__":
    sys.exit(run(main))
