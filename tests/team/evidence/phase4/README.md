# Phase 4 defensive security evidence

Use the [native rerun evidence](native/README.md) for submission. The original ZAP HTML and dependency HTML below are historical derived summaries. ZAP generated the new HTML and JSON. The new pip-audit JSON comes directly from the tool.

Phase 4 evaluated the local Flask/Vue appointment workflows with Chromium and ZAP 2.17.0. The run passed eight browser tests. The passive scan observed 141 messages and reported 61 instances across ten rule IDs. pip-audit recorded 103 records across five of 99 installed packages. Aliases reduce the records to 71 advisory groups.

| Evidence | Files |
|---|---|
| Scope, actual routes and models | [Attack surface](attack-surface.md), [environment and reproduction](environment.md), [actual tool versions](tool-versions.json), [protected development database hashes](integrity.json) |
| Browser scripts and executed reports | [Tests](../../phase4/test_security_decisions.py), [HTML](playwright.html), [JUnit](playwright.xml), [log](playwright.log.txt) |
| Individual access decisions | [P4-01](P4-01.json), [P4-02](P4-02.json), [P4-03](P4-03.json), [P4-04](P4-04.json), [P4-05](P4-05.json), [P4-06](P4-06.json), [P4-07](P4-07.json) |
| Access and transport controls | [Matrix and controller checks](access-control.md), [transport evidence](transport.json) |
| Proxy and passive ZAP run | [Runner](../../tools/phase4_passive.py), [configuration and versions](zap-config.json), [daemon log](zap-daemon.log.txt), [run totals and queue](zap-run.json), [observed methods/statuses](zap-observed-requests.json) |
| ZAP passive findings | [JSON](zap-alerts.json), [HTML summary](zap-summary.html), [HTML by instance](zap-alerts.html) |
| Python dependency audit | [Tool metadata and exit](pip-audit-run.json), [log](pip-audit.log.txt), [actual JSON](pip-audit.json), [installed versions](installed-packages.json), [dependency summary](dependency-summary.html), [advisory groups and audited packages](dependency-advisories.html) |
| Uncropped browser screenshots | [Booking](screenshots/P4-01.png), [Cancellation](screenshots/P4-03.png), [Doctor booking actual account screen](screenshots/P4-02.png), [Doctor cancellation actual account screen](screenshots/P4-04.png), [Nonowner](screenshots/P4-05.png), [Anonymous](screenshots/P4-06.png), [Doctor readback](screenshots/P4-07.png) |
| Uncropped screenshots of rendered report evidence | [Doctor booking denial](screenshots/P4-02-response.png), [Doctor cancellation denial](screenshots/P4-04-response.png), [ZAP summary](screenshots/zap-summary.png), [ZAP detail viewport](screenshots/zap-alerts.png), [Dependency summary](screenshots/dependency-summary.png) |
| Consolidated findings and assessment | [Register](findings.md), [Section 4 compliance](../../../../docs/team/phase4-compliance.md), [Word report](../../../../docs/team/MediHub_SQE_Continuous_Report_Verified.docx) |

The HTML reports open locally in a browser after downloading the file. The ZAP reports render captured passive alert metadata. Denial evidence renders the observed response and SQLite assertion from each test, alongside separate original Chromium captures of the account screens. No credentials, token values or raw request/response bodies are retained in the evidence.
