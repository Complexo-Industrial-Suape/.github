#!/usr/bin/env python3
"""HTTP security headers auditor.

Companion to skill `checking-http-security-headers`. Probes the target
GET response and grades each canonical security header.

Checks performed:
    1. Strict-Transport-Security — presence, max-age, includeSubDomains, preload
    2. Content-Security-Policy — presence, unsafe-inline, unsafe-eval,
       frame-ancestors
    3. X-Frame-Options — present OR CSP frame-ancestors set
    4. X-Content-Type-Options:nosniff
    5. Referrer-Policy — present, not unsafe-url
    6. Permissions-Policy
    7. Server: header version disclosure
    8. Cache-Control on authenticated endpoint

References:
    MDN — HTTP security headers
    OWASP Secure Headers Project (https://owasp.org/www-project-secure-headers/)
    Mozilla Observatory
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib.authz_check import require_authorization  # noqa: E402
from lib.finding import Finding, Severity  # noqa: E402
from lib.http_client import make_session, safe_get  # noqa: E402
from lib.report import EXIT_ERROR, emit, exit_code, run  # noqa: E402

SKILL_ID = "checking-http-security-headers"

PRELOAD_MIN_MAX_AGE = 31536000  # 1 year (hstspreload.org requirement)
REDIRECT_STATUSES = (301, 302, 303, 307, 308)


def _check_hsts(headers: dict, target: str, is_https: bool) -> list[Finding]:
    findings: list[Finding] = []
    if not is_https:
        return findings
    hsts = headers.get("Strict-Transport-Security")
    if not hsts:
        return [
            Finding(
                skill_id=SKILL_ID,
                title="Strict-Transport-Security header missing",
                severity=Severity.HIGH,
                target=target,
                detail=(
                    "No HSTS header on the HTTPS response. The first time a "
                    "client visits the site over HTTPS (or any first-visit after "
                    "their HSTS cache expires), an attacker on the network can "
                    "rewrite the response to use HTTP — and clients have no "
                    "pinning to refuse the downgrade."
                ),
                remediation=(
                    "Add: `Strict-Transport-Security: max-age=31536000; "
                    "includeSubDomains; preload`. nginx: `add_header "
                    'Strict-Transport-Security "max-age=31536000; '
                    'includeSubDomains; preload" always;`.'
                ),
                cwe_id="CWE-319",
                owasp_category="A05:2021",
                references=("https://hstspreload.org/",),
            )
        ]
    # Parse max-age
    m = re.search(r"max-age\s*=\s*(\d+)", hsts)
    if m:
        max_age = int(m.group(1))
        if max_age < PRELOAD_MIN_MAX_AGE:
            findings.append(
                Finding(
                    skill_id=SKILL_ID,
                    title=f"HSTS max-age ({max_age}s) below preload threshold",
                    severity=Severity.MEDIUM,
                    target=target,
                    detail=(
                        f"HSTS max-age is {max_age}s. hstspreload.org requires "
                        f"≥{PRELOAD_MIN_MAX_AGE}s (1 year) for preload-list "
                        "submission."
                    ),
                    remediation=f"Increase max-age to {PRELOAD_MIN_MAX_AGE}.",
                )
            )
    if "includesubdomains" not in hsts.lower():
        findings.append(
            Finding(
                skill_id=SKILL_ID,
                title="HSTS without includeSubDomains",
                severity=Severity.LOW,
                target=target,
                detail=(
                    "Subdomains are not covered by the HSTS policy, so a "
                    "downgrade on any of them can still set or read cookies "
                    "scoped to the parent domain. hstspreload.org also requires "
                    "includeSubDomains for preload submission."
                ),
                remediation="Add `includeSubDomains` to the HSTS header value.",
            )
        )
    return findings


def _check_csp(headers: dict, target: str) -> list[Finding]:
    findings: list[Finding] = []
    csp = headers.get("Content-Security-Policy")
    if not csp and headers.get("Content-Security-Policy-Report-Only"):
        return [
            Finding(
                skill_id=SKILL_ID,
                title="Content-Security-Policy is report-only",
                severity=Severity.MEDIUM,
                target=target,
                detail=(
                    "Only Content-Security-Policy-Report-Only is set. The browser "
                    "reports violations but blocks nothing, so the policy gives "
                    "no XSS protection yet."
                ),
                remediation=(
                    "Once the violation reports settle, serve the same policy "
                    "under `Content-Security-Policy`."
                ),
                cwe_id="CWE-79",
                owasp_category="A03:2021",
            )
        ]
    if not csp:
        return [
            Finding(
                skill_id=SKILL_ID,
                title="Content-Security-Policy header missing",
                severity=Severity.HIGH,
                target=target,
                detail=(
                    "No CSP. The browser will execute any inline script the "
                    "server (or any injection vector) returns. Reflected and "
                    "stored XSS classes are unmitigated."
                ),
                remediation=(
                    "Start with a report-only policy: "
                    "`Content-Security-Policy-Report-Only: default-src 'self'; "
                    "report-uri /csp-report`. Move to enforcing once violations "
                    "settle. See references/PLAYBOOK.md § CSP rollout."
                ),
                cwe_id="CWE-79",
                owasp_category="A03:2021",
            )
        ]
    if "'unsafe-inline'" in csp:
        findings.append(
            Finding(
                skill_id=SKILL_ID,
                title="CSP includes 'unsafe-inline'",
                severity=Severity.MEDIUM,
                target=target,
                detail=(
                    "'unsafe-inline' permits inline <script> and onclick= "
                    "handlers. This is the most common XSS-protection bypass."
                ),
                remediation=(
                    "Replace inline handlers with addEventListener; replace "
                    "inline styles with classes; if migration is gradual, use "
                    "nonce-source or hash-source CSP entries per script block."
                ),
                cwe_id="CWE-79",
                owasp_category="A03:2021",
            )
        )
    if "'unsafe-eval'" in csp:
        findings.append(
            Finding(
                skill_id=SKILL_ID,
                title="CSP includes 'unsafe-eval'",
                severity=Severity.MEDIUM,
                target=target,
                detail=(
                    "'unsafe-eval' permits eval(), new Function(), and similar. "
                    "Most modern frameworks (React/Vue/Angular in production "
                    "mode) don't need this."
                ),
                remediation=(
                    "Audit dependencies for eval usage; replace or upgrade. "
                    "Common offenders: older Angular dev mode, older Vue "
                    "with template-runtime."
                ),
            )
        )
    return findings


def _check_clickjacking(headers: dict, target: str) -> list[Finding]:
    xfo = headers.get("X-Frame-Options", "").strip().lower()
    csp = (headers.get("Content-Security-Policy") or "").lower()
    if xfo in ("deny", "sameorigin") or "frame-ancestors" in csp:
        return []
    if xfo:
        # ALLOWALL was never standard and ALLOW-FROM is ignored by current
        # browsers: both leave the page frameable.
        return [
            Finding(
                skill_id=SKILL_ID,
                title=f"X-Frame-Options:{xfo} gives no clickjacking protection",
                severity=Severity.HIGH,
                target=target,
                detail=(
                    f"X-Frame-Options is set to `{xfo}`, a value browsers do not "
                    "enforce, and CSP frame-ancestors is absent. The page can be "
                    "embedded in an attacker's iframe."
                ),
                remediation=(
                    "Use `X-Frame-Options: DENY` or `SAMEORIGIN`, or "
                    "`Content-Security-Policy: frame-ancestors` for selective embedding."
                ),
                cwe_id="CWE-1021",
            )
        ]
    return [
        Finding(
            skill_id=SKILL_ID,
            title="No clickjacking protection (X-Frame-Options + frame-ancestors both absent)",
            severity=Severity.HIGH,
            target=target,
            detail=(
                "Neither X-Frame-Options nor CSP frame-ancestors is set. The "
                "page can be embedded in an attacker's iframe and used for "
                "UI-redress (clickjacking) attacks against authenticated "
                "users."
            ),
            remediation=(
                "Add `X-Frame-Options: DENY` for pages never embedded, or "
                "`Content-Security-Policy: frame-ancestors 'self' "
                "https://embedded-by.example.com` for selective embedding."
            ),
            cwe_id="CWE-1021",
        )
    ]


def _check_nosniff(headers: dict, target: str) -> list[Finding]:
    if headers.get("X-Content-Type-Options", "").lower() == "nosniff":
        return []
    return [
        Finding(
            skill_id=SKILL_ID,
            title="X-Content-Type-Options:nosniff missing",
            severity=Severity.MEDIUM,
            target=target,
            detail=(
                "Without nosniff, browsers may MIME-sniff a response served "
                "as text/plain and execute it as JavaScript if it looks "
                "script-shaped. Closes a class of file-upload XSS."
            ),
            remediation="Add `X-Content-Type-Options: nosniff` to every response.",
            cwe_id="CWE-79",
        )
    ]


def _check_referrer(headers: dict, target: str) -> list[Finding]:
    rp = headers.get("Referrer-Policy", "").lower()
    if not rp:
        return [
            Finding(
                skill_id=SKILL_ID,
                title="Referrer-Policy missing",
                severity=Severity.MEDIUM,
                target=target,
                detail=(
                    "Without a Referrer-Policy, the browser uses no-referrer-"
                    "when-downgrade by default — internal URLs leak to external "
                    "sites the user navigates to."
                ),
                remediation=("Add `Referrer-Policy: strict-origin-when-cross-origin` (the modern recommendation)."),
            )
        ]
    if rp in ("unsafe-url",):
        return [
            Finding(
                skill_id=SKILL_ID,
                title=f"Referrer-Policy:{rp} leaks full URL cross-origin",
                severity=Severity.MEDIUM,
                target=target,
                detail="unsafe-url sends the full URL to every cross-origin destination.",
                remediation="Change to `strict-origin-when-cross-origin`.",
            )
        ]
    return []


def _check_permissions_policy(headers: dict, target: str) -> list[Finding]:
    if headers.get("Permissions-Policy"):
        return []
    return [
        Finding(
            skill_id=SKILL_ID,
            title="Permissions-Policy header missing",
            severity=Severity.LOW,
            target=target,
            detail=(
                "Without Permissions-Policy, the browser permits the page to "
                "request all device capabilities (camera, mic, geo, USB, "
                "serial). On a public-content page these should be denied by "
                "default."
            ),
            remediation=(
                "Add `Permissions-Policy: camera=(), microphone=(), "
                "geolocation=(), interest-cohort=()` (deny-all baseline)."
            ),
        )
    ]


CROSS_ORIGIN_HEADERS = (
    (
        "Cross-Origin-Opener-Policy",
        Severity.LOW,
        "Without COOP a cross-origin page that opens this one keeps a window "
        "reference to it, which enables cross-window leaks (XS-Leaks).",
        "Add `Cross-Origin-Opener-Policy: same-origin`.",
    ),
    (
        "Cross-Origin-Resource-Policy",
        Severity.LOW,
        "Without CORP any site can embed this response as a no-cors "
        "subresource, which exposes it to speculative-execution side channels.",
        "Add `Cross-Origin-Resource-Policy: same-origin` (or `same-site`).",
    ),
    (
        "Cross-Origin-Embedder-Policy",
        Severity.INFO,
        "COEP is only required for cross-origin isolation (SharedArrayBuffer, "
        "high-resolution timers). Absence is not a weakness by itself.",
        "Add `Cross-Origin-Embedder-Policy: require-corp` if the page needs cross-origin isolation.",
    ),
)


def _check_cross_origin_isolation(headers: dict, target: str) -> list[Finding]:
    return [
        Finding(
            skill_id=SKILL_ID,
            title=f"{name} header missing",
            severity=severity,
            target=target,
            detail=detail,
            remediation=remediation,
        )
        for name, severity, detail, remediation in CROSS_ORIGIN_HEADERS
        if not headers.get(name)
    ]


def _check_content_type(headers: dict, target: str) -> list[Finding]:
    content_type = headers.get("Content-Type", "")
    if "html" in content_type.lower():
        return []
    return [
        Finding(
            skill_id=SKILL_ID,
            title=f"Response is not HTML ({content_type or 'no Content-Type'})",
            severity=Severity.INFO,
            target=target,
            detail=(
                "CSP, X-Frame-Options and Permissions-Policy protect rendered "
                "documents. On a JSON API or a download, their absence matters "
                "less; HSTS, nosniff and Cache-Control still apply."
            ),
            remediation="Read the document-oriented findings with this in mind.",
        )
    ]


def _check_server_disclosure(headers: dict, target: str) -> list[Finding]:
    server = headers.get("Server", "")
    if re.search(r"\d+\.\d+", server):
        return [
            Finding(
                skill_id=SKILL_ID,
                title=f"Server header discloses version: {server}",
                severity=Severity.LOW,
                target=target,
                detail=(
                    "The Server header includes a version number, letting "
                    "fingerprinters target known CVEs in that exact version."
                ),
                remediation=(
                    "nginx: `server_tokens off;`. "
                    "Apache: `ServerTokens Prod`. "
                    "Caddy: omit version by default (Caddy 2.x doesn't disclose)."
                ),
                cwe_id="CWE-200",
            )
        ]
    return []


def _check_cache_control(headers: dict, target: str, authenticated: bool) -> list[Finding]:
    cc = headers.get("Cache-Control", "").lower()
    if authenticated and ("public" in cc or "max-age" in cc and "private" not in cc and "no-store" not in cc):
        return [
            Finding(
                skill_id=SKILL_ID,
                title="Authenticated endpoint allows shared caching",
                severity=Severity.HIGH,
                target=target,
                detail=(
                    "Authenticated content with public-cacheable Cache-Control "
                    "can be served by shared caches (CDN, corporate proxy) to "
                    "different users — one user's authenticated response leaks "
                    "to another."
                ),
                remediation=("Set `Cache-Control: private, no-store` on every authenticated endpoint."),
                cwe_id="CWE-525",
            )
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HTTP security headers auditor")
    parser.add_argument("url")
    parser.add_argument("--authorized", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--format", choices=("json", "jsonl", "markdown"), default="markdown")
    parser.add_argument("--min-severity", choices=("critical", "high", "medium", "low", "info"), default="info")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--authenticated", action="store_true", help="Apply stricter Cache-Control checks")
    args = parser.parse_args(argv)

    require_authorization(args.url, args.authorized)

    sess = make_session(timeout=args.timeout)
    resp = safe_get(sess, args.url, timeout=args.timeout)
    if resp is None:
        sys.stderr.write(f"ERROR: target {args.url!r} unreachable\n")
        return EXIT_ERROR

    target = args.url
    redirect_note: list[Finding] = []
    location = resp.headers.get("Location")
    if resp.status_code in REDIRECT_STATUSES and location:
        destination = urllib.parse.urljoin(args.url, location)
        same_host = urllib.parse.urlparse(destination).hostname == urllib.parse.urlparse(args.url).hostname
        followed = safe_get(sess, destination, timeout=args.timeout) if same_host else None
        if followed is not None:
            resp, target = followed, destination
        else:
            # The authorization covers the host that was named, not wherever it redirects.
            redirect_note.append(
                Finding(
                    skill_id=SKILL_ID,
                    title=f"Response is a redirect to {destination} (not followed)",
                    severity=Severity.INFO,
                    target=target,
                    detail="The headers graded below are those of the redirect response itself.",
                    remediation="Re-run against the destination URL if you are authorized to test it.",
                )
            )

    is_https = target.lower().startswith("https://")
    # Header names are case-insensitive; keep the response's own mapping.
    headers = resp.headers

    findings: list[Finding] = list(redirect_note)
    findings.extend(_check_content_type(headers, target))
    findings.extend(_check_hsts(headers, target, is_https))
    findings.extend(_check_csp(headers, target))
    findings.extend(_check_clickjacking(headers, target))
    findings.extend(_check_nosniff(headers, target))
    findings.extend(_check_referrer(headers, target))
    findings.extend(_check_permissions_policy(headers, target))
    findings.extend(_check_cross_origin_isolation(headers, target))
    findings.extend(_check_server_disclosure(headers, target))
    findings.extend(_check_cache_control(headers, target, args.authenticated))

    floor = Severity(args.min_severity)
    findings = [f for f in findings if f.severity.numeric >= floor.numeric]

    emit(findings, args.output, args.format, target)
    return exit_code(findings)


if __name__ == "__main__":
    sys.exit(run(main))
