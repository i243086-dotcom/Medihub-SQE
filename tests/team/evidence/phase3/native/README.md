# Phase 3 source-native rerun

Executed on Windows with Flask/Vue on 127.0.0.1:5001, synthetic accounts, a disposable SQLite database and controlled January 2030 booking data. Both audits used Chrome 158.0.8127.88, 1440×1000 desktop, Lighthouse 12.8.2 snapshot mode, Playwright for Node 1.61.0, @axe-core/playwright 4.11.1 and axe-core 4.11.4. Chromium workflow tests used Python 3.11.9, Playwright 1.65.2, pytest 9.2.0 and pytest-html 4.2.0. The base was `0b15192775519ff7f7d605560bfeb1677eac471a`. The integrated corrected application was `436c9ff1b6d9fd29c717be719ec187ce0b93f37d`. Both audit processes exited 0.

| Native result | Before | After |
|---|---|---|
| Chromium, 2 passed each, exit 0 | [pytest-html](before/pytest.html), [JUnit](before/pytest.xml), [log](before/pytest.log.txt) | [pytest-html](after/pytest.html), [JUnit](after/pytest.xml), [log](after/pytest.log.txt) |
| Booking Lighthouse user flow | [HTML](before/lighthouse-flow-booking.html), [JSON](before/lighthouse-flow-booking.json), [authenticated context](before/context-booking.json) | [HTML](after/lighthouse-flow-booking.html), [JSON](after/lighthouse-flow-booking.json), [authenticated context](after/context-booking.json) |
| Cancellation Lighthouse user flow | [HTML](before/lighthouse-flow-cancellation.html), [JSON](before/lighthouse-flow-cancellation.json), [authenticated context](before/context-cancellation.json) | [HTML](after/lighthouse-flow-cancellation.html), [JSON](after/lighthouse-flow-cancellation.json), [authenticated context](after/context-cancellation.json) |
| Booking AxeBuilder full results | [JSON](before/axe-booking.json) | [JSON](after/axe-booking.json) |
| Cancellation AxeBuilder full results | [JSON](before/axe-cancellation.json) | [JSON](after/axe-cancellation.json) |
| Supplementary deduplication | [Rerun matrix and exact element mappings](findings.json) | [Historical explanatory register](../findings.md) |
| Native audit logs | [Before](before/audit.log.txt) | [After](after/audit.log.txt) |
| Original images from the rerun | [Before](screenshots/before/) | [After](screenshots/after/) |

The export calls are `flow.snapshot()`, `flow.createFlowResult()` and `flow.generateReport()` in [phase3_audits.mjs](../../../tools/phase3_audits.mjs). The four additional `lighthouse-<screen>.html/.json` files are unchanged native per-snapshot exports from the same flow. Snapshot HTML shows counts of applicable passing checks, while the weighted category scores below come from Lighthouse's own JSON. AxeBuilder results are unchanged apart from JSON serialization, with all four result arrays and metadata. There is no native standalone axe-core HTML report. Each pytest-html report also embeds the matching original JSON as an attachment. [Official Lighthouse user-flow API](https://github.com/GoogleChrome/lighthouse/blob/main/docs/user-flows.md)

| Authenticated screen | Accessibility | Best Practices | SEO | Axe rules / elements | Unique tool findings |
|---|---:|---:|---:|---:|---:|
| Booking before | 85 | 100 | 60 | 7 / 17 | 19 |
| Booking after | 91 | 100 | 60 | 5 / 9 | 11 |
| Cancellation before | 89 | 100 | 60 | 6 / 10 | 12 |
| Cancellation after | 89 | 100 | 60 | 6 / 10 | 12 |

All measurements match the historical runs. Booking still rejects the occupied slot, explains the correction and completes another booking by keyboard. Cancellation persists after reload. The corrected UI gives keyboard access to specialty and doctor buttons. Desktop automated snapshots describe the observed states.

Reproduce with the [environment setup](../environment.md), set `MEDIHUB_TESTED_COMMIT` and pass a fresh output directory to the existing server and audit runner. Run `python -m pytest tests/team/phase3 --browser chromium --tracing on --output <private-temp-dir> --html=<stage>/pytest.html --self-contained-html --junitxml=<stage>/pytest.xml` with `MEDIHUB_PHASE3_ATTACHMENTS` pointing to the current stage directory and `MEDIHUB_PHASE3_SHOTS` to its screenshot directory. Set `MEDIHUB_PHASE3_FIXED=1` only for the corrected source. Four genuine traces were retained in the run's private temporary directory because trace network and action data can contain credentials and tokens.
