# Phase 4 consolidated findings and residual risk

ZAP observed 141 HTTP messages from the sole scoped loopback site, including POST booking and DELETE cancellation with HTTP 200. The passive queue drained to 0. ZAP reported 61 instances across ten rule IDs. Repeated URL instances and confidence variants are grouped below. The local test exercised ordinary requests. Application-level exploitability and production infrastructure are unassessed.

| ID and scope | Actual evidence | Severity and confidence | Impact and proposed correction | Status and residual risk |
|---|---|---|---|---|
| P4-C01 appointment authorization | 7 decisions passed, including denied actions with unchanged SQLite. [Matrix](access-control.md) | Control verified, high confidence | Preserve patient/doctor guards, appointment ownership and assigned readback regression. | Verified for selected cases, linked to R03. |
| P4-C02 token and origin behavior | Header JWT, zero auth cookies and no CORS grant in the observed preflight. [Transport](transport.json) | Control verified, high confidence | Preserve explicit authentication and avoid permissive credentialed CORS. | Verified within scoped origin and routes. |
| P4-F01 CSP and framing, app shell and preflight | ZAP 10038, 2 instances, and 10020, 1 instance. CSP and framing headers absent. [Headers](zap-observed-requests.json) | Medium, high for CSP and medium for framing | Browser lacks script restrictions and anti-framing policy. Trial CSP in report-only mode, then enforce a compatible policy with frame-ancestors. Use legacy X-Frame-Options as appropriate. | Open, browser defense-in-depth. |
| P4-F02 third-party resource trust, app shell | ZAP 90003, 2 instances, and 10017, 1 instance. External references visible in `frontend/index.html`. | Medium/high for integrity, low/medium for inclusion | Third-party assets expand the supply-chain boundary. Pin or self-host eligible resources and review which third-party scripts are required. | Open. No third-party site was scanned. |
| P4-F03 missing nosniff | ZAP 10021, 20 instances. [Alert rows](zap-alerts.html) | Low, medium | Browser MIME sniffing can create avoidable content-handling risks. Set X-Content-Type-Options and confirm correct types. | Open. |
| P4-F04 Server header | ZAP 10036, 25 instances. [Alert rows](zap-alerts.html) | Low, high | Reveals development stack and version. Use a supported production server and minimise version disclosure on the public edge. | Confirmed locally. Production configuration unassessed. |
| P4-F05 comments | ZAP 10027, 4 instances in HTML and frontend scripts. [Alert rows](zap-alerts.html) | Informational, low or medium | Review flagged nonessential client comments before production build. This assessment found no confirmed credential exposure in the recorded metadata. | Informational triage. |
| P4-I01 stack and session identification | ZAP 10109, 10111 and 10112, 6 instances combined. [Alert rows](zap-alerts.html) | Informational, medium or high | Expected application, authentication and session-response discovery. Browser and source establish explicit JWT headers. | Observation, no vulnerability inferred. |
| P4-F06 localStorage and logout | Token storage and removal in `frontend/js/api.js`, logout handler has no server revocation. [Source](../../../../backend/routes/auth.py) · [Browser observation](transport.json) | Medium potential impact, high confidence in source behavior | Same-origin JavaScript can read the token. A copied token can remain valid until expiry under the observed design. Review shorter sessions, revocation and token storage with an explicit CSRF model. | Open design risk. No token theft or replay test performed. |
| P4-F07 transport and cache defaults | HTTP is used on loopback and the observed booking/cancellation API responses lacked Cache-Control. [Proxy records](zap-observed-requests.json) | Context-dependent, high confidence locally | Require deployed HTTPS and review application or edge enforcement of no-store for sensitive responses. Validate production headers separately. | Deployment configuration unassessed. |

## Python advisories

pip-audit completed with exit 1 for findings. It audited 99 installed packages and skipped none. The service returned 103 records across five packages. Alias union within each package gives 71 advisory groups. The [complete inventory and advisory IDs](dependency-advisories.html) lists all packages, all observed aliases and advisory-listed fixed releases. Risk below reflects app relevance, rather than assigning CVSS that the audit did not return.

| ID and installed package | Advisory groups | Triage and confidence | Impact and remediation |
|---|---:|---|---|
| P4-D01 Flask 2.3.3 | 1 | High priority, high inventory confidence | Core request stack. Evaluate the advisory-listed Flask 3.1.3 and test upgrade compatibility. |
| P4-D02 Werkzeug 2.3.7 | 8 | High priority, high inventory confidence | WSGI and request handling. Evaluate Werkzeug 3.1.9, the highest listed fix, alongside Flask. |
| P4-D03 Flask-CORS 4.0.0 | 5 | Medium if used, high inventory confidence | Runtime pin with no direct app import found. Remove if unused. Otherwise review 6.0.0, the highest listed fix, and separately triage records with no fix version. |
| P4-D04 Pillow 10.1.0 | 52 | Medium pending reachability, high inventory confidence | Image parsing can affect availability and image handling if reachable. No direct backend PIL import was found. Verify transitive usage before removing, or check Pillow 13.0.0 compatibility and rerun the audit. |
| P4-D05 setuptools 65.5.0 | 5 | Medium build risk, high inventory confidence | Packaging infrastructure. Evaluate setuptools 84.1.0 and isolate package installation. |

Use the advisory versions as inputs to an upgrade plan, verify compatible versions and rerun the audit against the resolved environment. Public rollout remains on hold pending triage of affected dependencies and review of production transport and browser defenses. No production-code changes were made during Phase 4. See [Phase 2 risks](../../../../docs/team/phase2-defect-and-risk-report.md#residual-risk-assessment-and-exit-control).

Remediation tracking is open for [dependency advisories (#14)](https://github.com/i243086-dotcom/Medihub-SQE/issues/14) and [browser hardening (#15)](https://github.com/i243086-dotcom/Medihub-SQE/issues/15).
