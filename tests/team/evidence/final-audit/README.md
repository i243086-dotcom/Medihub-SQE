# Final correction evidence index

The run uses integrated application source 50554b9aefbf514bc4998aed1bedd20441f793f3 plus the API-only minute-boundary test. No existing tool artifacts were overwritten. The fixtures use disposable SQLite and check the development database hash. Production source and CI configuration are unchanged.

The local pytest command was:

    .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q -s -o junit_family=legacy tests/team/unit tests/team/api --cov=backend --cov-branch --cov-report=json:<temporary-report> --junitxml=tests/team/evidence/final-audit/functional.xml

- [Original pytest JUnit](functional.xml) contains 729 passed tests, including the seven new API probes, the Phase 5 recovery regression, and both original unit and remaining API suites. No test failures or skips.
- [Original coverage.py JSON](functional-coverage.json) is the combined correction measurement. It records 972/1170 statements and 261/372 branch arcs. The historical 720/720 scoped statements and 234/234 scoped arcs come from the existing Phase 2 unit archive.
- [Traditional MCC matrix](mcc-traditional.csv) is a derived view of the native unit verdicts and exact expectations asserted on each executed test.
- [Per-case API audit](api-per-case-audit.csv) is a derived join of the committed cases, original native API properties and the added minute-edge results.
- [Technical audit](../../../../docs/team/PHASE2_FINAL_TECHNICAL_AUDIT.md) explains scope, decisions, coverage, exact generator commands, cases and recorded limits.
- [Archived Phase 3–5 checks](archived-phase-checks.json) show values rechecked against original reports without rerunning their workloads.
- [Word layout verification](word-layout.json) records the final native Word page count and image extent and crop measurements.

Both generator outputs were reproduced byte-for-byte against the Git files. Checksums:

- appointment_cases.json SHA-256 cfe5b7cf8eeda8cbba7ea17f1142609270724f52a71a3c29318cd4722171c702
- appointment_cases_proposed.json SHA-256 58fc67ac911b39da767b4e10d4a97e305ea85516c56aaaedcadf8269a2c2cf35

Phase 2 human screenshot capture is pending. See the [capture guide](../../../../docs/team/PHASE2_MANUAL_SCREENSHOT_GUIDE.md).
