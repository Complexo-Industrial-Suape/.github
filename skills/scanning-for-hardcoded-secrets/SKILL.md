---
name: scanning-for-hardcoded-secrets
description: |
  Scan a source-code tree for hardcoded credentials embedded in source
  files: AWS access keys, GitHub tokens, Stripe keys, Slack tokens,
  Anthropic API keys, OpenAI keys, JWT signing secrets, generic
  base64-encoded passwords, RSA / SSH private keys, and high-entropy
  string literals that pattern-match common credential shapes.
  Use when: pre-commit gate before pushing a feature branch, audit
  before SOC2, post-incident scan after a leak, or inheriting a
  codebase you didn't write.
  Threshold: any source file contains a string that matches a
  canonical credential regex (AWS AKIA prefix, GitHub ghp_ prefix,
  etc.) OR a string with Shannon entropy at or above 3.5 in a field
  context (key=, token:, secret=).
  Trigger with: "scan secrets", "credential scan", "find hardcoded
  keys", "leak check".
allowed-tools:
  - Read
  - Bash(python3:*)
  - Glob
  - Grep
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
  - Bash(wget:*)
  - Write(.env)
  - Edit(.env)
version: 3.30.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - static-analysis
  - secrets
  - pentest
---

# Scanning for Hardcoded Secrets

## Overview

The single most common cause of credential breach in 2026 remains
hardcoded secrets in source code. Engineers paste an API key into a
config file "just for testing," forget to remove it, commit the
file. The credential is now in the repository's history forever
(`git rebase` doesn't help if anyone cloned in between) and
extractable by anyone who reaches the repo: contractors,
ex-employees, attackers via `.git/` directory exposure (see skill
six), GitHub bot scrapers crawling public repos.

The cost of detection-after-commit is near-zero (free tools exist:
gitleaks, trufflehog, this skill). The cost of detection-before-commit
is also near-zero (pre-commit hooks). The cost of remediation after
the fact is rotating every credential exposed + auditing for
exploitation + potentially notifying customers of breach. The
asymmetry is severe, the discipline is the only constraint.

This skill scans a filesystem tree, matching against a canonical
regex library covering the credential shapes attackers and bots
search for first.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| AWS access key (AKIA-prefix) | **CRITICAL** | Literal `AKIA[0-9A-Z]{16}` in any file | CWE-798 |
| AWS secret access key | **CRITICAL** | 40-char base64 in `aws_secret_access_key` field context | CWE-798 |
| GitHub personal access token | **CRITICAL** | `ghp_[A-Za-z0-9]{36}` or `gho_`, `ghu_`, `ghs_`, `ghr_` | CWE-798 |
| GitHub app installation token | **CRITICAL** | `ghs_[A-Za-z0-9]{36}` | CWE-798 |
| Stripe live key | **CRITICAL** | `sk_live_[A-Za-z0-9]{24,}` | CWE-798 |
| Stripe test key | **MEDIUM** | `sk_test_[A-Za-z0-9]{24,}` | CWE-798 |
| Anthropic API key | **CRITICAL** | `sk-ant-api03-[A-Za-z0-9_-]{93}` or similar | CWE-798 |
| OpenAI API key | **CRITICAL** | `sk-(proj-)?[A-Za-z0-9_-]{40,}` | CWE-798 |
| Slack bot token | **CRITICAL** | `xoxb-[A-Za-z0-9-]+` | CWE-798 |
| Slack user token | **CRITICAL** | `xoxp-[A-Za-z0-9-]+` | CWE-798 |
| Google API key | **HIGH** | `AIza[A-Za-z0-9_-]{35}` | CWE-798 |
| RSA / OpenSSH private key | **CRITICAL** | BEGIN PRIVATE KEY header (RSA, OPENSSH, EC, DSA variants) | CWE-321 |
| JWT secret | **HIGH** | Long string in `jwt_secret`, `JWT_SECRET`, `signing_secret` field | CWE-321 |
| Generic password literal | **HIGH** | `password = "..."` with a quoted, non-placeholder value of 8+ characters and entropy ≥ 3.0 | CWE-798 |
| High-entropy string in key/token field | **MEDIUM** | 20+ characters with at least one digit and Shannon entropy ≥ 3.5 (`--entropy-threshold`) in a `*key` / `*token` field | CWE-798 |
| Credential file committed | per match above | `.env*`, `id_rsa`, `*.pem`, `*.key`, `.npmrc`, `.pypirc`, `.netrc` are read by name, even without a source extension | CWE-200 |

## Prerequisites

- Python 3.9+
- Target source-code tree on local filesystem
- `git` on PATH, only for `--git-history`
- On Windows, run the scripts with `python` instead of `python3`

## Instructions

### Step 1 — Identify the scan target

This skill scans a filesystem path. No authorization gate (it
operates on local source code, not network targets).

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/scanning-for-hardcoded-secrets/scripts/scan_secrets.py /path/to/repo
```

Options:

```
Usage: scan_secrets.py PATH [OPTIONS]

Options:
  --output FILE      Write findings to FILE (default: stdout)
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --include-tests    Include files under tests/, test/, __tests__/, spec/
                     (default: excluded to reduce false positives)
  --git-history N    Also scan the last N git commits' diffs (default: 0
                     = working tree only)
  --exclude GLOB     Skip files matching glob (repeatable)
  --entropy-only     Only flag entropy-based findings (skip regex)
  --entropy-threshold N
                     Minimum Shannon entropy for field-context findings
                     (default: 3.5)
```

The scanner walks the tree, applies the regex library to every
candidate file, and emits a Finding per match with file path, line
number, severity, and the redacted matched text. `PATH` may also be a
single file. With `--git-history N` it also scans the lines added by
the last N commits; those findings are labelled `git:<sha>:<path>`.

A value followed by `(`, `.` or `[` is treated as a function call or
attribute access, not a literal, and is skipped.

### Step 3 — Interpret findings

CRITICAL = the matched string is a real credential shape that
upstream tools auto-extract. Rotate the credential immediately.
Audit logs for any API call against that credential since the
commit landed.

HIGH = pattern strongly suggests credential but requires manual
verification (the literal might be a placeholder or test fixture).

MEDIUM / LOW = entropy-based heuristic that needs human review.

### Step 4 — Remediation

For any confirmed real credential:

1. **Rotate immediately.** Don't wait to refactor; the leak window
   is between when the commit landed and when you rotate.
2. **Audit usage.** Check provider's API logs for any unfamiliar
   calls against that credential since the leak commit timestamp.
3. **Remove from source.** Move to environment variables, secrets
   manager, or a runtime-provisioned secret. See
   `references/PLAYBOOK.md` for per-language patterns.
4. **Scrub history if reasonable.** `git filter-repo` or `BFG
   Repo-Cleaner` can purge the secret from history, but only if you
   can force-push and coordinate with every clone-holder. For
   public repos, history-scrub is often not worth the disruption
   compared to just rotating.

## Examples

### Example 1 — Pre-commit gate

```bash
# .git/hooks/pre-commit (or via pre-commit framework)
python3 skills/scanning-for-hardcoded-secrets/scripts/scan_secrets.py \
    --min-severity high --format json . | jq -e 'length == 0' \
    || { echo "Secrets detected. Fix before commit."; exit 1; }
```

### Example 2 — CI scan on every push

```yaml
- name: Hardcoded-secrets scan
  run: |
    python3 skills/scanning-for-hardcoded-secrets/scripts/scan_secrets.py \
        . --min-severity high --format json --output secrets-scan.json
- run: |
    if jq 'length > 0' secrets-scan.json | grep -q true; then
      echo "::error::Hardcoded secret detected"
      exit 1
    fi
```

### Example 3 — Audit inherited codebase

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/scanning-for-hardcoded-secrets/scripts/scan_secrets.py \
    /path/to/acquired-repo --include-tests --min-severity medium
```

`--include-tests` is important here because legacy test fixtures
often contain real credentials someone forgot to redact.

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit codes: 0 clean, 1
high/critical, 2 error.

Matched strings are partially redacted in output (first 4 + last 4
chars visible, middle redacted) to avoid the scanner output itself
becoming a leak surface.

## Error Handling

- **False positive on placeholder strings** like `<YOUR_KEY_HERE>` →
  the scanner skips strings containing `<`, `>`, `EXAMPLE`,
  `PLACEHOLDER`, `YOUR_`, `XXXX` (fixed list in the script).
- **Binary or unknown file in tree** → skipped. Files are selected by
  extension and by well-known credential file names, not by content.
- **Path does not exist, or `--git-history` outside a git repository**
  → exit 2.
- **Large file** → files >5 MB are skipped (avoids scanning compiled
  artifacts and lockfiles).

## Resources

- `references/THEORY.md` — Per-credential-family threat model, why
  each provider's keys are extracted by bots first, history-scrub
  decision framework, entropy-detection theory
- `references/PLAYBOOK.md` — Per-language migration patterns
  (Python dotenv, Node .env+dotenv, Ruby Rails credentials, Go
  envconfig), provider rotation procedures, GitHub secret-scanning
  integration

---

## Freedom Calibration (MUST vs CONSIDER)

- **Mandatory Standards (MUST / NEVER)**:
  - MUST scan commit history (`--git-history N`) as well as the working tree: a secret deleted from the tree is still in history.
  - MUST classify real leaked API keys or private keys as Critical severity.
  - NEVER print raw high-entropy secret values into public logs or pull request comments.
- **Flexible Guidance (SHOULD / CONSIDER)**:
  - SHOULD use pre-commit hooks (`gitleaks`, `detect-secrets`) to prevent secret commits.
  - CONSIDER entropy scoring alongside pattern matching to detect unformatted tokens.

---

## Secret Scan Verification Checklist

Before approving code for commit:
- [ ] Have all `.env*` files been verified to be excluded by `.gitignore`?
- [ ] Has regex pattern matching scanned for standard cloud keys (AWS AKIA, GitHub ghp_, Stripe sk_)?
- [ ] Have high-entropy string literals been checked and relocated to environment variables?
- [ ] If a secret was detected in history, has the token been immediately revoked at the provider?
