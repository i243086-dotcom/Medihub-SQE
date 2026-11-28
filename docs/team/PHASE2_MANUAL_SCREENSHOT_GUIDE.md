# Phase 2 manual screenshot guide

Capture these images yourself on Windows. All entries below start **pending capture**. The reconstructed Word report contains the textual result and evidence references. Capture from the current CI artifacts when useful, and keep historical snapshots distinctly labeled. The figure index in §14.6 reserves caption numbers without inserting empty images.

## Common Windows setup and capture

1. Open PowerShell at D:\SQE_Project\Medihub. Set the following variables. Open the files in a browser or VS Code without resaving native reports.

       $py = (Resolve-Path '.venv\Scripts\python.exe').Path
       $v = 'tests/team/evidence/phase2/independent-closure/final-ci'
       $out = 'tests/team/evidence/final-audit/screenshots'
       New-Item -ItemType Directory -Force $out | Out-Null
       & $py --version
       Get-Command code, gh, docker -ErrorAction SilentlyContinue

2. Maximize the chosen window. Use browser zoom or VS Code zoom until labels and results are readable together. Include the tool or artifact name and the distinguishing commit, report title or run ID where possible. Do not show logins, tokens or private data.
3. Press **Win + Shift + S**, select **Window snip** for the whole app window or select the full report panel with **Rectangular snip**, and open the Snipping Tool preview. Press **Ctrl+S**, choose PNG and save using the exact name below in **tests/team/evidence/final-audit/screenshots/**. For wide evidence, use two separately named PNGs. Preserve the PNG as captured.
4. Open each saved file in Photos at 100%. Check that all intended columns, axes, numbers and legends are visible and readable. Compare with the source or run. Record the source path/URL and revision in the caption or adjacent text. When inserting, fit the complete PNG inside the existing Word margins with locked aspect ratio and no crop.

## P2-01 SonarQube metrics and ratings

- **Tool and availability:** SonarQube Community Build 26.11.0.134175, pysonar 1.11.0.6012 and a browser. Confirm with **docker ps**, **& .\.venv\Scripts\pysonar.exe --version** and the UI footer or saved scanner log.
- **Launch and services:** MediHub need not run. The local dashboard requires the existing Sonar/Docker service. Start Docker Desktop from Start only if you intend to use it. Verify the existing container with **docker ps --filter publish=9001**. If stopped, identify it with **docker ps -a --filter publish=9001**, then **docker start <existing-container-name>**. Keep it loopback-only. Do not overwrite the project or start a replacement scan for a historical screenshot.
- **Open and click:** **http://127.0.0.1:9001/dashboard?id=medihub-phase2-candidate**. Click **Activity** to identify the scan/revision, then **Overview** and **Measures** for ratings, issues, duplication, coverage and complexity. A live local project may show a different analysis. If that happens, open the saved **tests/team/evidence/phase2/release-gate/ci-sonar.json** in VS Code. Expand **raw → component → measures**, **native_gate** and **analysis_history**. The file is a native API snapshot displayed in VS Code. The CI loopback URL is not a public dashboard.
- **Expected:** Historical CI revision **30a918b00b7cd29696a94f37539b42e60778d0d1** records Security A, Reliability A, 1.1% duplication, 44.6% combined coverage and native gate OK. A locally displayed revision may have different values. Match the revision before labeling it. **Fresh run:** no.
- **Save:** **P2-01-sonarqube.png**. Caption **Figure 2.1. SonarQube metrics and ratings with the analyzed revision identified.** Insert in **§14.1**. Confirm the revision and scope are legible.

## P2-02 coverage.py and scoped totals

- **Tool and availability:** coverage.py 7.17.4 and VS Code. Confirm **& $py -m coverage --version**. Use HTML in the browser and the scope JSON in VS Code.
- **Launch and services:** MediHub and Sonar/Docker may be off. Open **$v/unit/htmlcov/index.html** in Edge or Chrome. Click **Files** and then **backend/routes/patient.py** for the native coverage report. Open **$v/unit/scoped.json** in VS Code using **code "$v/unit/scoped.json"**. Expand **scope_totals**. The JSON is the scope extraction, while the HTML is native coverage.py.
- **Expected:** The scope record displays **720/720 statements and 234/234 branch arcs**. The native HTML uses the full-file denominator and may display different totals.
- **Fresh run:** no. If the native report is absent, record a new run in a temporary path only.

       $tmp = Join-Path $env:TEMP ('medihub-p2-cov-' + (Get-Date -Format yyyyMMddHHmmss))
       New-Item -ItemType Directory $tmp | Out-Null
       & $py -m pytest -p no:cacheprovider tests/team/unit -q --cov=backend --cov-branch --cov-report="json:$tmp/coverage.json" --cov-report="html:$tmp/htmlcov"
       & $py tests/team/tools/phase2_metrics.py coverage "$tmp/coverage.json" "$tmp/scoped.json" --enforce

- **Save:** **P2-02-coverage.png**, optionally **P2-02b-scoped.png**. Caption **Figure 2.2. Native coverage.py and the separate appointment-scope statement and branch counts.** Insert in **§14.1**. Keep the denominator labels visible.

## P2-03 MCC and MC/DC

- **Tool and availability:** pytest 9.2.0, native JUnit, and VS Code. Confirm **& $py -m pytest --version** and **Get-Command code**.
- **Launch and services:** Neither MediHub nor Sonar/Docker is needed. Click **File → Open File** in VS Code and open **$v/unit/unit.xml**, **$v/unit/br02-mcc.csv** and **$v/unit/br02-mcdc.csv**. Search for **MCC-111111**. Open **tests/team/evidence/final-audit/mcc-traditional.csv** for the academic T/F view. Show the JUnit case and original pairs in separate snips if needed. CSV displays are supporting evidence.
- **Expected:** Original execution covers **64 unique cases**, and the pair file lists **six pairs using seven combinations**. Compare the all-true row and each one-false row. **Fresh run:** no. For a new terminal excerpt only, use **& $py -m pytest -p no:cacheprovider tests/team/unit/test_appointment_rules.py -k br02_all_combinations -v**.
- **Save:** **P2-03-mcc-mcdc.png**, optionally **P2-03b-mcc-native.png**. Caption **Figure 2.3. Executed booking decision combinations and independent MC/DC pairs.** Insert in **§14.2**. Keep column labels and original IDs in frame.

## P2-04 EP/BVA generation

- **Tool and availability:** Python 3.11.9, OpenAPI generator and VS Code. Confirm **& $py --version** and **& $py tests/team/tools/generate_appointment_cases.py --help**.
- **Launch and services:** Neither MediHub nor Sonar/Docker is needed. Open **tests/team/data/appointments.openapi.yaml**, **tests/team/data/appointment_cases.json** and **tests/team/evidence/final-reconstruction/ep-bva-matrix.csv**. Use **Ctrl+F** for **GEN-book-body-appointment_time-12-59** and then open the source overlay. Show terminal generation beside original data.
- **Expected and command:** A fresh generator run is appropriate here. It is data-only and writes to temporary files. The active run prints **1.4.0: 262 generated cases**. Compare hashes and label the other output proposed.

       $a = Join-Path $env:TEMP ('medihub-p2-active-' + [Guid]::NewGuid().ToString('N') + '.json')
       $b = Join-Path $env:TEMP ('medihub-p2-proposed-' + [Guid]::NewGuid().ToString('N') + '.json')
       & $py tests/team/tools/generate_appointment_cases.py tests/team/data/appointments.openapi.yaml $a
       & $py tests/team/tools/generate_appointment_cases.py tests/team/data/appointments.openapi.yaml $b --overlay tests/team/data/appointments.proposed-v2.yaml
       Get-FileHash $a,tests/team/data/appointment_cases.json,$b,tests/team/data/appointment_cases_proposed.json

- **Save:** **P2-04-ep-bva-generator.png**. Caption **Figure 2.4. Deterministic OpenAPI test-case generation and an original EP/BVA case.** Insert in **§14.3**. Show the command, version and raw case ID.

## P2-05 API/integration pytest report

- **Tool and availability:** pytest 9.2.0 and VS Code. Confirm **& $py -m pytest --version**.
- **Launch and services:** Neither service is needed. Open **$v/api/api.xml** in VS Code. Click the opening testsuite, then **Ctrl+F** for **test_concurrent_booking_integrity** or **rows_before**. Format XML for display only if needed without saving. For the correction, open **tests/team/evidence/final-reconstruction/functional.xml** and search **GEN-book-body-appointment_time-09-01**.
- **Expected:** Historical **336 tests**, zero failures/errors/skips. Later acceptance is 372 API plus 430 unit. The correction report combines **802 unit/API tests**, so label it separately, and show the actual HTTP and row properties. **Fresh run:** no.
- **Save:** **P2-05-pytest-api.png**. Caption **Figure 2.5. Native API JUnit result with acceptance, rejection and persisted-state checks.** Insert in **§14.3**. Use two shots if the test identity and row status cannot fit in one.

## P2-06 Playwright browser flows

- **Tool and availability:** Playwright Python 1.65.2, pytest-playwright and pytest-html 4.2.0. Confirm **& $py -m playwright --version** and **& $py -m pip show pytest-html**. Chrome or Edge can read a saved report without launching Chromium.
- **Launch and services:** Neither service is needed. Open **$v/browser/browser.html**. Show **30 passed**, then filter or search **uc01** through **uc06** and expand representative flow output. Use **$v/browser/browser.xml** for exact nodes. This is pytest-html output from a Playwright suite.
- **Expected:** **30 pass**, zero failed or skipped. Confirm representative **N, A1, A2, E1, E2** IDs and saved screenshots. **Fresh run:** no.
- **Save:** **P2-06-playwright-flows.png**. Caption **Figure 2.6. Executed Chromium use-case flows with their native pytest result and postcondition assertions.** Insert in **§14.4**. Keep report totals, suite identity and readable case rows.

## P2-07 Cosmic Ray

- **Tool and availability:** Cosmic Ray 8.9.0. Confirm **& .\.venv\Scripts\cosmic-ray.exe --version**.
- **Launch and services:** Neither service is needed. In VS Code open **$v/mutation/summary.json**, **$v/mutation/cosmic-report.txt** and **$v/mutation/CM-01.txt** and **CM-02.txt**. Expand **cosmic**, then show **killed**, **survived**, **score** and the two custom statuses.
- **Expected:** **144 killed, 2 surviving, 146 executed; 98.63%**, both custom operators killed. The score keeps the two equivalent survivors in the denominator. **Fresh run:** no. If a demonstration is required, **& $py tests/team/tools/phase2_mutation.py "$env:TEMP/medihub-mutation-viva" --enforce** runs in a disposable source copy. Use a new path.
- **Save:** **P2-07-cosmic-ray.png**. Caption **Figure 2.7. Cosmic Ray mutation score and the two killed custom operators.** Insert in **§14.5**. Include raw operator or run identity where readable.

## P2-08 blocked GitHub Actions run

- **Tool and availability:** Browser and GitHub Actions. Optional **gh --version**. Sign in only if prompted. MediHub and local Sonar/Docker are unnecessary.
- **Launch and click:** Open [run 45662563964](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45662563964). Click **Summary**, **SonarQube full scan** and **Loopback deployment demonstration**. Original saved state is **tests/team/evidence/phase2/release-gate/deployment-blocked-run.json**.
- **Expected:** Sonar failed and preview was skipped on PR #11's tested head **1ba21e8**. Use **gh run view 45662563964** if the job graph is collapsed. **Fresh run:** no.
- **Save:** **P2-08-actions-blocked.png**. Caption **Figure 2.8. Failed Sonar gate and skipped loopback preview on the original PR run.** Insert in **§14.5**. Keep run ID and failed/skipped outcomes visible.

## P2-09 corrected passing GitHub Actions run

- **Tool and availability:** Browser/GitHub Actions. Optional **gh --version**. Neither local service is needed.
- **Launch and click:** Open [run 45663975402](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45663975402), click **Summary** and view six required jobs plus the loopback preview. For the input-specific fix also open [before](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45217711369/job/137843248708) and [after](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45218777165/job/137847005597). Use **gh run view 45663975402** if necessary.
- **Expected:** All six jobs and loopback preview pass. Booking regression moves from **3 failed plus 1 pass to 4 pass** in the linked earlier pair. **Fresh run:** no.
- **Save:** **P2-09-actions-passing.png**. Caption **Figure 2.9. Passing protected checks and successful local preview on the corrected revision.** Insert in **§14.5**. Include run ID and candidate context.

## P2-10 representative issue and RCA

- **Tool and availability:** Browser/GitHub Issues and VS Code. Check **Get-Command code** or open the Markdown directly. Neither service is needed.
- **Launch and click:** Open [Issue #5](https://github.com/i243086-dotcom/Medihub-SQE/issues/5). Show title, current state and fix-verified label. In VS Code open **docs/team/DEFECT_LIFECYCLE_AND_GQM.md** and **docs/team/phase2-defect-and-risk-report.md**. Search **#5**, then show the booked-only root cause and evidence.
- **Expected:** Rebooking defect is high/high and fix-verified in the audited state. If the issue state changes by capture time, use the actual visible issue state and caption date. **Fresh run:** no.
- **Save:** **P2-10-issue-rca.png**, optionally **P2-10b-rca-source.png**. Caption **Figure 2.10. Recorded rebooking defect, current tracking state and verified RCA.** Insert in **§15**. Retain issue number and links.

Optional **P2-11-booking-readback.png** may show a genuine existing UC03 or UC05 browser screenshot beside the native case. Open the original from **$v/browser/screenshots/** and identify the exact test ID. Neither service nor rerun is required. Caption **Figure 2.11. Booking or cancellation screen and its linked SQLite postcondition.** Insert in **§14.4**.

## Capture and insertion checklist

| Figure | Capture | Insert and verify |
|---|---|---|
| P2-01 Sonar | Pending | §14.1, verify revision |
| P2-02 Coverage | Pending | §14.1, verify both denominators |
| P2-03 MCC/MC/DC | Pending | §14.2, verify original IDs |
| P2-04 Generator | Pending | §14.3, verify active vs proposed |
| P2-05 API | Pending | §14.3, verify run scope and row evidence |
| P2-06 Browser | Pending | §14.4, verify total and flow identities |
| P2-07 Mutation | Pending | §14.5, verify denominator and custom kills |
| P2-08 Blocked run | Pending | §14.5, keep failure and skip visible |
| P2-09 Passing run | Pending | §14.5, keep run ID and all jobs visible |
| P2-10 Issue/RCA | Pending | §15, quote the actual visible issue state |
