# Phase 4 compliance

This checklist covers Section 4, page 4 of the official SQE assignment and the corresponding six-mark rubric. The [full evidence index](../../tests/team/evidence/phase4/README.md) lists the reports and source, while the [continuous Word report](MediHub_SQE_Continuous_Report_Verified.docx) carries the measured conclusions and original figures.

| Requirement | Status | Executed evidence |
|---|---|---|
| Identify the routes, parameters and data used in both workflows | PASS | [Attack-surface inventory](../../tests/team/evidence/phase4/attack-surface.md) |
| Run the real application with synthetic users and an isolated database | PASS | [Environment](../../tests/team/evidence/phase4/environment.md) and [development database hashes](../../tests/team/evidence/phase4/integrity.json) |
| Record an expected and observed two-role access-control matrix | PASS | [Seven decisions](../../tests/team/evidence/phase4/access-control.md) |
| Execute at least four allowed and denied browser decisions with SQLite readbacks | PASS | [Chromium tests](../../tests/team/phase4/test_security_decisions.py), [HTML](../../tests/team/evidence/phase4/playwright.html) and [JUnit](../../tests/team/evidence/phase4/playwright.xml) |
| Capture both workflows in a localhost ZAP passive session | PASS | [Proxy configuration](../../tests/team/evidence/phase4/zap-config.json), [141 observed messages](../../tests/team/evidence/phase4/zap-observed-requests.json), [proxy log](../../tests/team/evidence/phase4/zap-daemon.log.txt) |
| Wait for passive processing and report alert severity/confidence | PASS | [Drain result](../../tests/team/evidence/phase4/zap-run.json), [JSON alerts](../../tests/team/evidence/phase4/zap-alerts.json), [HTML details](../../tests/team/evidence/phase4/zap-alerts.html) |
| Corroborate two security controls with real observations and source | PASS | [JWT/role/ownership and transport controls](../../tests/team/evidence/phase4/access-control.md), [CORS and cookie results](../../tests/team/evidence/phase4/transport.json) |
| Run an open-source dependency audit with resolved package versions | PASS | [Actual pip-audit result](../../tests/team/evidence/phase4/pip-audit.json), [command and exit code](../../tests/team/evidence/phase4/pip-audit-run.json), [inventory and advisories](../../tests/team/evidence/phase4/dependency-advisories.html) |
| Record affected components, impact, fixes and residual risk | PASS | [Deduplicated findings](../../tests/team/evidence/phase4/findings.md), [issue #14](https://github.com/i243086-dotcom/Medihub-SQE/issues/14), [issue #15](https://github.com/i243086-dotcom/Medihub-SQE/issues/15) |
| Provide automatically captured original images and report evidence | PASS | [Screenshot index](../../tests/team/evidence/phase4/README.md) |
| Append Section 4 and original full-size figures to the continuous report | PASS | [Word report sections 19.1–19.6](MediHub_SQE_Continuous_Report_Verified.docx) |

All eight Chromium cases passed. The dependency audit completed with findings and exit 1. The assessment is complete for the tested local workflows. Open findings and deployment checks keep public rollout on hold.
