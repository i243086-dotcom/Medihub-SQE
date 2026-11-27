# Phase 5 evidence index

The measured source is the MediHub application merged in [PR #16](https://github.com/i243086-dotcom/Medihub-SQE/pull/16), at commit `305918fd27941004bf59766e559937a009ca8eda`. All measurements and recovery actions used synthetic data and localhost.

- [Targets and success contract](targets.md), [committed configuration](targets.json), [k6 workload](../../phase5/availability.js) and [isolated runner](../../phase5/run.py).
- [Environment and database safeguards](environment.md), [machine inventory](machine.json), [official installer and executable verification](k6-installation.json).
- [Performance comparison](results.md), [machine-readable derived results](results.json), [analysis script](../../phase5/analyze.py) and [database safety](runs/database-safety.json).
- [Recovery test](../../api/test_phase5_booking_recovery.py), [actual SQLite states and HTTP responses](recovery/state.json), [command and exit](recovery/run.json), [pytest terminal](recovery/pytest.log), [native JUnit](recovery/junit.xml) and [pytest-html report](recovery/pytest.html). The existing API CI job discovers the test.
- [Section 5 compliance](compliance.md) and [continuous report](../../../../docs/team/MediHub_SQE_Continuous_Report_Verified.docx).

## Final matched series

Every run configuration records the actual command, executable, program revision, build, timings, initial and final database hashes, dashboard probe, and process exit. The console, JSONL streams and HTML exports are original k6 output. The machine-readable legacy summaries retain the original metrics and redact only the private `setup_data` token array.

| Run | Native HTML | Console | Native JSON metric stream | Summary | Provenance and Flask log |
| --- | --- | --- | --- | --- | --- |
| P5-L01 | [Dashboard](runs/P5-L01/dashboard.html) | [Terminal](runs/P5-L01/console.log) | [JSONL](runs/P5-L01/metrics.jsonl) | [Redacted JSON](runs/P5-L01/summary.redacted.json) | [Run](runs/P5-L01/run.json) · [Flask](runs/P5-L01/flask.log) |
| P5-L02 | [Dashboard](runs/P5-L02/dashboard.html) | [Terminal](runs/P5-L02/console.log) | [JSONL](runs/P5-L02/metrics.jsonl) | [Redacted JSON](runs/P5-L02/summary.redacted.json) | [Run](runs/P5-L02/run.json) · [Flask](runs/P5-L02/flask.log) |
| P5-L03 | [Dashboard](runs/P5-L03/dashboard.html) | [Terminal](runs/P5-L03/console.log) | [JSONL](runs/P5-L03/metrics.jsonl) | [Redacted JSON](runs/P5-L03/summary.redacted.json) | [Run](runs/P5-L03/run.json) · [Flask](runs/P5-L03/flask.log) |
| P5-L04 | [Dashboard](runs/P5-L04/dashboard.html) | [Terminal](runs/P5-L04/console.log) | [JSONL](runs/P5-L04/metrics.jsonl) | [Redacted JSON](runs/P5-L04/summary.redacted.json) | [Run](runs/P5-L04/run.json) · [Flask](runs/P5-L04/flask.log) |

[One-user dashboard PNG](screenshots/P5-L01-dashboard.png) · [Five-user dashboard PNG](screenshots/P5-L04-dashboard.png) · [Native terminal thresholds PNG](screenshots/P5-L04-k6-terminal.png) · [pytest result PNG](screenshots/recovery-pytest.png). Playwright 1.65.2 with Chromium 159.0.8154.6 captured all four original viewport PNGs from genuine reports using [capture.py](../../phase5/capture.py). The Word report embeds the full files.

## Initial series and retry

The [initial series](initial-series/) used the official Windows portable binary, whose SHA-256 matched the subsequently installed executable. It completed L01 and L02. L03 exited 107 after a synthetic login timed out in setup, with zero steady-state requests. L04 did not start. The original runner attempted a port bind while Windows retained closed TCP connections in TIME_WAIT. [L03 console](initial-series/P5-L03/console.log) · [L03 provenance](initial-series/P5-L03/run.json).

The final series used one fresh matched snapshot across all four trials and the native installation. It increases only the login setup timeout and checks for live port listeners. The endpoint, measured 2-second request timeout, run duration, VU levels, fixture layout and predeclared thresholds are the same. Earlier valid measurements and the interrupted attempt remain archived.

## Reproduce on this Windows checkout

Use the established Python virtual environment. Open two PowerShell windows in the checkout and leave ports 5001 and 5665 free. The first command below runs all four trials. For a single demonstration add `--run P5-L01`. Use a fresh output path every time.

```powershell
& 'C:\Program Files\k6\k6.exe' version
& .\.venv\Scripts\python.exe tests/team/phase5/run.py --k6 'C:\Program Files\k6\k6.exe' --output "$env:TEMP\medihub-phase5-demo"
```

While k6 runs, open its built-in [dashboard](http://127.0.0.1:5665) in Chrome, for example with `Start-Process chrome.exe 'http://127.0.0.1:5665'`. This is the browser interface provided by k6 OSS, whose primary interface is its CLI. Close the live tab after viewing so its connection can end normally. After the run, open any saved `dashboard.html` directly in Chrome. GitHub may show the exported HTML as source. The downloaded file runs in a local browser. The dashboard aggregates all phases. The comparison table reports only the tagged steady operation.

```powershell
& .\.venv\Scripts\python.exe tests/team/phase5/analyze.py tests/team/evidence/phase5/runs
$recovery = Join-Path $env:TEMP 'medihub-phase5-recovery-demo'
New-Item -ItemType Directory -Force $recovery | Out-Null
$env:MEDIHUB_P5_RECOVERY_EVIDENCE = Join-Path $recovery 'state.json'
& .\.venv\Scripts\python.exe -m pytest -v -s tests/team/api/test_phase5_booking_recovery.py --junitxml "$recovery\junit.xml" --html "$recovery\pytest.html" --self-contained-html
```

Reproduction writes unmodified native summaries in a private temp directory printed by the runner. The local final-series and initial-series originals contain only short-lived synthetic tokens from torn-down instances. Keep them out of Git and external reports.
