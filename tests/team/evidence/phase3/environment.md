# Phase 3 environment and reproduction

Runs completed on Windows on 27 November 2026 (PKT). The real Flask application served the existing Vue frontend and patient REST endpoints on loopback at `http://127.0.0.1:5001/`. The app used the original SPA route with `#book` and `#patient-appointments` visible only after login.

## Source and data isolation

| Item | Recorded value |
|---|---|
| Verified baseline application commit | `0b15192775519ff7f7d605560bfeb1677eac471a`, the merged Phase 2 tree |
| Original upstream tag target | `baseline-v0^{}` = `e58ce855f5fb0c725ece13fa0a44d25486078465` |
| Tested original JS and CSS Git blobs | `a581ea2d145ac40a8427ec2cac6958bc0f9d1423`, `0ea3bef187c30881ddb5c977403d5684c3d65b0f` |
| Tested updated JS and CSS Git blobs | `dc2e732a1c04af0b4b40f6bd8135510930cb7f8f`, `0e456f6de05d909dfd62c5ddf3be26b76d76af7c` |
| Browser fixtures | Per-case disposable in-memory SQLite with a random JWT secret, blocked SMTP and suppressed mail. The harness refuses any other database URI. |
| Lighthouse and axe fixture | Per-run SQLite file under a temporary directory, engine path asserted before seeding. The Flask server stops and the temporary directory is cleaned on exit. Mail is suppressed. |
| Test patients and doctors | Patient fixture `arjun` uses the browser. Patient fixture `vikram` creates the competing 09:00 slot. Cardiology doctor ID 1 and Neurology doctor ID 2 are synthetic active doctors. |
| Dates and appointments | Model clock fixed to 15 January 2030. Booking and cancellation use 16 January 2030. Both doctors have seeded morning and evening availability. Cancellation starts with a Booked 10:00 appointment. |
| Protected development DB SHA-256, before and after | `27be0512bd93cfadb49d7819cff68fe6088334b50b1d2f5a9489d488df6554f5` |
| Playwright case runtime | Python 3.11.9, pytest 9.2.0, Playwright 1.65.2, pytest-playwright 0.10.0, pytest-html 4.2.0, shipped Chromium 159.0.8154.6, 1280 × 720 |
| Audit runtime | Node.js 22.16.0, Chrome 158.0.8127.88, Lighthouse 12.8.2, Playwright for Node 1.61.0, `@axe-core/playwright` 4.11.1 with axe-core 4.11.4, Puppeteer Core 24.37.5, 1440 × 1000 |
| Server packages | Flask 2.3.3 and SQLAlchemy 2.1.9 |

Baseline evidence was first captured before the correction. The final baseline archive rerun used application files from the exact baseline commit and the same Phase 3 test and audit scripts as the corrected run. The archive omitted the development database. The corrected run's logs show the protected development database digest before and after. Both audit runners use identical settings on each before/after pair. The reports contain the synthetic display names and task data. The evidence excludes login screens, passwords and live session secrets.

Microsoft Word 16.0 paginated the cumulative report at 34 pages. The full Word export was rendered and reviewed. The Phase 3 evidence is on pages 27–34 with ten embedded PNG figures. The original 112 report body blocks, containing the cover and earlier phases, matched the archived report XML.

## Run the Chromium cases

Use the project test environment and the existing pinned Vue and Bootstrap cache used by the Phase 2 browser fixture. That fixture verifies the three asset SHA-256 values. The audit also needs the Bootstrap Icons 1.11.0 CSS and WOFF2 from the URLs in the runner. Run from the repository root in PowerShell.

```powershell
$e = 'tests/team/evidence/phase3'
$env:MEDIHUB_BROWSER_ASSETS = Join-Path $env:TEMP 'medihub-phase1-browser-assets'
$env:MEDIHUB_PHASE3_SHOTS = "$e/screenshots/after"
$env:MEDIHUB_PHASE3_FIXED = '1'
.venv/Scripts/python.exe -m pytest tests/team/phase3 --browser chromium --html="$e/after/playwright.html" --self-contained-html --junitxml="$e/after/playwright.xml"
```

To reproduce the original run, archive `backend`, `frontend`, `tests/team/conftest.py`, `tests/team/phase2_support.py` and `tests/team/e2e` from the baseline commit into a temporary folder and copy `tests/team/phase3` and the audit scripts there. Run within that source using the existing Python interpreter. Unset `MEDIHUB_PHASE3_FIXED` and direct the artifacts to the baseline output. The two cases cover the original task behavior and the additional corrected-state assertions when the flag is set.

## Run the authenticated audits

```powershell
$env:MEDIHUB_AUDIT_MODULES = Join-Path $env:TEMP 'medihub-phase3-audit'
npm install --prefix $env:MEDIHUB_AUDIT_MODULES playwright@1.61.0 @axe-core/playwright@4.11.1 lighthouse@12.8.2 puppeteer-core@24.37.5
$env:MEDIHUB_CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
$env:MEDIHUB_PHASE3_TEST_PASSWORD = (.venv/Scripts/python.exe -B -c "import sys;sys.path[:0]=['backend','tests/team'];from phase2_support import PASSWORD;print(PASSWORD)")
.venv/Scripts/python.exe tests/team/tools/phase3_audit_server.py node tests/team/tools/phase3_audits.mjs after $e
Remove-Item Env:MEDIHUB_PHASE3_TEST_PASSWORD
.venv/Scripts/python.exe tests/team/tools/phase3_findings.py
```

Use the same launcher with the archived source and the `before` argument for the baseline. Run browser cases and audits sequentially because they bind the same test port. The runner serves the pinned CDN assets from the local cache and blocks other external browser requests. Lighthouse runs the checks available in snapshot mode. Scores do not establish WCAG conformance or screen-reader behavior.
