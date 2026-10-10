---
name: auditing-python-dependencies
description: |
  Audit a Python project's installed dependencies for known CVEs by
  wrapping pip-audit (PyPA's official vulnerability auditor) and
  emitting findings in the canonical Finding schema.
  Detects vulnerable direct AND transitive packages, normalizes
  pip-audit's severity output via OSV severity bands, falls back to
  pip list --outdated when pip-audit isn't installed, and supports
  requirements.txt and pyproject.toml (PEP 621) as input sources;
  poetry.lock, Pipfile.lock and uv.lock must be exported first.
  Use when: pre-merge gate on a Python project, post-incident sweep
  after a PyPI compromise (e.g. ctx, request-toolbelt typosquats,
  ultralytics 8.3.42 compromise), SOC2 evidence collection, or
  inheriting an unfamiliar Python codebase.
  Threshold: any HIGH or CRITICAL CVE in the resolved dependency
  tree. MODERATE / LOW reported informationally.
  Trigger with: "audit python deps", "pip vulnerability scan",
  "check pypi packages for CVEs", "pip-audit run".
allowed-tools:
  - Read
  - Bash(pip:*)
  - Bash(pip-audit:*)
  - Bash(python3:*)
  - Glob
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
  - Bash(wget:*)
  - Write(.env)
  - Edit(.env)
  - Bash(pip install:*)
  - Bash(pip uninstall:*)
version: 3.30.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - dependency-audit
  - python
  - pypi
  - cve
  - pentest
---

# Auditing Python Dependencies

## Overview

PyPI hosts north of 500,000 packages, with several thousand new
releases every day. The package-install model is identical to npm in
the relevant ways: a `pip install` resolves a transitive graph,
runs each package's `setup.py` (which executes arbitrary Python at
install time), and writes the result to your site-packages. The CVE
attack surface is therefore the same shape: known vulnerabilities,
maintainer-account takeovers, typosquats, and protestware.

The PyPA-blessed auditor is `pip-audit`. It queries the Open Source
Vulnerabilities (OSV) database (which mirrors PyPA's advisory feed
plus aggregated CVE / GHSA records) and reports per-package
vulnerable versions. `pip-audit` reads `requirements.txt` files and
projects described by `pyproject.toml`. It does not read `poetry.lock`,
`Pipfile.lock` or `uv.lock`; export those to a requirements file first.

This skill wraps `pip-audit`, normalizes its severity vocabulary to
the shared `Severity` enum, and emits Findings in the canonical
Finding schema. If `pip-audit` isn't installed on the
host, the skill falls back to `pip list --outdated` and emits
INFO-level findings recommending the operator install pip-audit
for accurate vulnerability detection.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Critical CVE in installed package | **CRITICAL** | OSV severity band corresponds to CVSS ≥ 9.0 | CWE-1104 |
| High CVE in installed package | **HIGH** | OSV severity band corresponds to CVSS 7.0–8.9 | CWE-1104 |
| Medium CVE in installed package | **MEDIUM** | OSV severity band corresponds to CVSS 4.0–6.9 | CWE-1104 |
| Low CVE in installed package | **LOW** | OSV severity band corresponds to CVSS 0.1–3.9 | CWE-1104 |
| Vulnerable package with no patch | **HIGH** | finding has no `fix_versions` and severity ≥ medium | CWE-1395 |
| Advisory with no score | **HIGH** | pip-audit's JSON carries no severity; an unscored advisory blocks by default | CWE-1104 |
| Outdated package (no CVE) | **INFO** | pip list --outdated reports a newer version | (operational) |
| pip-audit not installed | **INFO** | binary not on PATH; scanner fell back to pip list | (operational) |
| Audit could not run | exit 2 | pip-audit timed out, could not reach the advisory service, or returned no JSON | (operational) |

OSV is the upstream of record. pip-audit also consults the PyPA
advisory database for Python-specific records that may not yet have
a CVE assigned.

## Prerequisites

- Python 3.9+
- `pip-audit` installed (`pip install pip-audit`); skill falls back
  to `pip list --outdated` if absent
- Target project containing `requirements*.txt` or `pyproject.toml`
- On Windows, run the scripts with `python` instead of `python3`
- Network access to OSV (`api.osv.dev`) and PyPI (`pypi.org`)

## Instructions

### Step 1 — Identify the scan target

Locate the project directory. The scanner picks its source in this order:

1. `requirements*.txt` at the project root. Files named for dev, test,
   docs or CI (`requirements-dev.txt`) are skipped unless `--include-dev`
   is passed.
2. `pyproject.toml`, audited as a project path, only when no
   requirements file exists. pip-audit resolves it in an isolated
   environment, which is slower.

A project that has only `poetry.lock`, `Pipfile.lock` or `uv.lock` is
rejected with exit 2 and the export command to run
(`poetry export -f requirements.txt`, `pipenv requirements`,
`uv export`). The scanner never audits the Python environment it runs
in: that would report on the wrong project.

### Step 2 — Run the audit

```bash
python3 ./scripts/audit_python.py /path/to/python-project
```

Options:

```
Usage: audit_python.py PATH [OPTIONS]

Options:
  --output FILE      Write findings to FILE (default: stdout)
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --requirement FILE Override auto-detection; specify a particular
                     requirements file (repeatable)
  --include-dev      Also audit requirements files named for dev, test,
                     docs or CI (default: skipped)
  --strict           Treat pip-audit warnings as errors
```

### Step 3 — Interpret findings

CRITICAL / HIGH = block release.

MEDIUM / LOW = track but don't block; many Python advisories report
edge-case theoretical issues that don't apply to your usage.

INFO = log only; e.g. "outdated but no known CVE" is information for
your release cadence, not a security action.

### Step 4 — Remediation

For a vulnerable package with `fix_versions`:

1. Bump the version pin in your requirements file:

   ```diff
   - requests==2.20.0
   + requests==2.31.0
   ```

2. Run `pip install -r requirements.txt --upgrade` (or
   `poetry lock --no-update && poetry update <pkg>`).

3. Run the test suite. CVE fixes occasionally include behavioral
   changes you didn't expect.

4. Commit the lock file diff alongside the requirements bump.

For a vulnerable transitive dep (one you didn't declare directly):

1. Find the parent: `pip show <vulnerable-package>` lists the parents
   in its "Required-by" line.

2. Check whether bumping the parent picks up the fix. `pip index
   versions <parent>` lists available versions.

3. If parent doesn't have a newer release that floors the vulnerable
   dep above the fix version, pin the transitive dep yourself in
   your requirements file. pip will use the more specific pin.

For a vulnerable package with NO fix available:

1. Subscribe to PyPA advisory notifications for that package.

2. If the vulnerability is exploitable in your usage, either
   replace the package or vendor + patch locally.

3. Document the exception in your security register with a
   re-evaluation date.

## Examples

### Example 1 — Pre-merge gate

```bash
python3 ./scripts/audit_python.py . --min-severity high --format json --output audit.json
jq -e '. == []' audit.json || { echo "High/critical Python CVE — fix before merge"; exit 1; }
```

### Example 2 — CI scan on every push

```yaml
- name: pip-audit
  run: pip install pip-audit
- name: Run audit
  run: |
    python3 skills/auditing-python-dependencies/scripts/audit_python.py \
        . --min-severity high --format markdown --output py-audit.md
```

### Example 3 — SOC2 evidence collection

```bash
mkdir -p evidence/CC7/
python3 ./scripts/audit_python.py . --include-dev --format json \
    --output evidence/CC7/py-audit-$(date +%Y%m%d).json
```

`--include-dev` for SOC2: include dev/test deps so auditors see the
full surface, not just production.

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit codes: 0 clean, 1
high/critical, 2 error.

Each Finding includes:

- `id` — `<skill-id>::<fingerprint>`, stable across runs for the same issue
- `title`, `severity` (critical / high / medium / low / info), `target`
- `detail` and `remediation`
- `cve_id`, `cvss_score`, `cwe_id` when known
- `evidence` — affected package, version or range, fix versions, advisory ID
- `references` — advisory and CVE URLs

## Error Handling

- **pip-audit not installed** → falls back to `pip list --outdated`
  and emits INFO Findings flagging the degraded scan. The fallback
  lists the Python environment running the scan, not the target
  project, and carries no CVE data.
- **No requirement file found** → exit 2, "no Python project structure
  recognized".
- **Advisory service unreachable, timeout, or malformed JSON** → exit 2
  with the first 500 characters of pip-audit's output. A scan that did
  not run is never reported as clean.

## Resources

- `references/THEORY.md` — PyPI supply-chain history, OSV vs NVD vs
  PyPA advisory scopes, why ecosystem-specific severity matters,
  Python-specific install-time risks (setup.py execution, eager
  dependency resolution), pip-audit vs Safety vs Snyk trade-offs
- `references/PLAYBOOK.md` — Per-toolchain remediation patterns
  (pip + requirements.txt, poetry, pipenv, uv, conda), monorepo /
  workspace scanning, override-equivalent patterns in Python
  ecosystem, GitHub Dependabot ecosystem mapping, SOC2 evidence
  retention

---

## Freedom Calibration (MUST vs CONSIDER)

- **Mandatory Standards (MUST / NEVER)**:
  - MUST inspect pinned requirements and lockfiles (`uv.lock`, `poetry.lock`, `requirements.txt`). The script reads `requirements*.txt` and `pyproject.toml`; export the lock formats first.
  - MUST flag any unpinned dependencies (`package>=1.0`) in production builds. This is a manual check: the script does not detect unpinned ranges.
  - NEVER run untrusted setup scripts without virtual environment isolation.
- **Flexible Guidance (SHOULD / CONSIDER)**:
  - SHOULD prefer `uv pip audit` or `pip-audit` for lightning-fast CVE matching.
  - CONSIDER automated Dependabot or Renovate pull requests for minor patches.

---

## Python Security Verification Checklist

Before declaring Python dependencies clean:
- [ ] Has a vulnerability database check (PyPA advisory DB / OSV) run cleanly?
- [ ] Are all dependencies pinned to deterministic versions via lockfiles?
- [ ] Are known vulnerable transitive sub-dependencies upgraded?
- [ ] Has the virtual environment been validated against malicious post-install hooks?
