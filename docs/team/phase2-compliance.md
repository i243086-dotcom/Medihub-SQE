# Section 2 compliance and evidence

**Release decision: HOLD.** The tested commit `9126fef` ran 560 cases with 556 passes and four failures. Unit 312/312, API and integration 214/218, and Chromium 30/30. No cases were skipped. Required API and Sonar checks are still failing, and the review branch remains unmerged.

## Verification-first reconciliation

The independent reviewer received the audit narrative, scripts and report. This local reconciliation loaded the missing raw evidence. [The per-ID comparison](../../tests/team/evidence/phase2/phase1_reaudit/run-03-comparison.csv) confirms 93 HTTP and one browser case per build, 67 passes, 12 failures and 15 policy-pending observations. Every verdict and recorded semantic observation matched after omitting timestamps and free-form failure prose. Archived runs were committed snapshots at `e58ce85` and `256efcb`. Both passed the browser confirmation/readback workflow at port 5001, with no SMTP attempt and identical development database hashes. The development UI at 5000 was unavailable during the audit.

The 12 failed cases were overlapping checks. One reproduced #5. Three used distinct invalid admin source-state fixtures for #7. Six checked input shape and type failures, including the effects recorded in #8–#10. Two checked a proposed exact-hour rule. The Stage D doctor reopening case failed its provisional assertion while the expanded comparison classified that observed behavior as policy pending. No H-06 definition was found.

The initial phase report's 11-point compact tables were inconsistent with the strict table typography. The cumulative report format and pagination are checked separately from the raw execution claims. Frozen historical dates and the controlled Phase 2 clock have distinct fixtures. A verbose development run displayed synthetic bearer values. Its artifacts were quarantined locally, the fixture representations were protected, and token-free reruns replaced it as distributable evidence.

## Rubric matrix

| Section 2 requirement | Status | Observed result and evidence |
|---|---|---|
| Planning, scope, risk-based depth and traceability | PASS | Workflows, owners proposed for confirmation, environment, case allocation, PERT, risk depth, risk matrix, exit comparisons and role-specific design recorded. [Test plan and use cases](phase2-test-design.md) · [Registry](../../tests/team/test_registry.csv) |
| Actual effort and team ownership | BLOCKED | 1.5 person-hours recorded. An actual total and confirmation of individual ownership require genuine member records. [Time log](../../tests/team/evidence/time_log.csv) |
| SonarQube real scan and coverage import | PASS | SonarQube Community Build 26.11.0.134175 and pysonar 1.11.0.6012 ran against MediHub. First scan had no coverage import. The final coverage-import analysis measured 904 complexity, 1.1% duplication, 21 smells, 15 bugs, 14 vulnerabilities, 41.0% combined project coverage, 78 minutes debt, maintainability A, reliability C and security E. [Initial export](../../tests/team/evidence/phase2/verification/sonar-before-project.json) · [Final export](../../tests/team/evidence/phase2/verification/sonar-release-thresholds.json) · [Dashboard](http://127.0.0.1:9000/dashboard?id=medihub-team) |
| Numbered CFG and Sonar comparison | PASS | Booking CFG has 89 edges, 68 nodes and one connected component. The conventional explicit-handler result is 23. Splitting Boolean short-circuit operands yields 28. Sonar reports 79 cyclomatic and 95 cognitive for the entire patient route file. Its component API exposed no measured value for the individual function, so a numeric function-to-function reconciliation remains unavailable. [CFG](../../tests/team/evidence/phase2/verification/booking-cfg.md) · [Sonar file data](../../tests/team/evidence/phase2/verification/sonar-after-patient-file.json) |
| Executed unit statement and branch coverage | PASS | The direct-handler and dependency suite passed **312** tests. The measured appointment scope reached **703/703 statements** and **226/226 branch arcs**. Scope is defined by deployed functions, models, decorators and dependencies. Repository-wide coverage has a different denominator. [Unit HTML](../../tests/team/evidence/phase2/verification/release/unit/htmlcov/index.html) · [Scope and denominator](../../tests/team/evidence/phase2/verification/release/unit/scoped.json) |
| Complete MCC, independent MC/DC and business-rule decisions | PASS | All 64 feasible BR-02 combinations executed. Every pair changes one predicate and the decision. Boundary, role and patient transition tests ran on real route logic. [MCC](../../tests/team/evidence/phase2/verification/release/br02-mcc.csv) · [MC/DC](../../tests/team/evidence/phase2/verification/release/br02-mcdc.csv) · [Decision tables](phase2-test-design.md) |
| Doctor/admin state-policy acceptance | BLOCKED | Unknown destinations and unassigned/wrong roles were exercised. Recognized source→destination policies need approval before binding their oracles. Issue #6 remains triaged. |
| OpenAPI validation and deterministic EP/BVA generator | PASS | Twelve operations and 196 active cases. The suite consumes generated data. Byte-identical rerun and missing-file detection verified. Two proposed constraint changes produced four changed expectations and four genuine proposed-contract failures. [OpenAPI](../../tests/team/data/appointments.openapi.yaml) · [Generation dependency](../../tests/team/evidence/phase2/verification/generated-input-required.txt) · [Variant matrix](../../tests/team/evidence/phase2/verification/generated-constraint-diff.csv) |
| API outcomes and shared-record readback | FAIL | All 196 generated active cases passed. The integration suite still exposes rebooking failure, two concurrent failures, and the historical provisional reopening assertion. [API coverage](../../tests/team/evidence/phase2/verification/api-coverage-matrix.csv) · [JUnit and row readbacks](../../tests/team/evidence/phase2/verification/release/suite/junit.xml) |
| Six use cases and every browser flow | PASS | All 30 Chromium scenarios passed on the updated build, including patient confirmations and persisted-state assertions. Two cases per proposed member. [Use cases](phase2-test-design.md) · [Actions browser job](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45218777165/job/137847006106) |
| Cosmic Ray and two custom operators | PASS | Initial run had 65 killed and 35 survivors across 100 executed candidates. After stronger assertions, the final tested commit recorded **116 killed, 2 surviving, 98.31%**, with both custom mutants killed. The two survivors are equivalent under the earlier past-date guard and first-split behavior. The gate keeps them in its conservative denominator. The line filter excluded 368 candidates outside the selected ranges. No timeout or incompetent mutant was in the final executed set. [Initial report](../../tests/team/evidence/phase2/verification/mutation-before/cosmic-report.txt) · [Survivor analysis](../../tests/team/evidence/phase2/verification/mutation-survivor-review.csv) · [Tested commit result](../../tests/team/evidence/phase2/verification/mutation-ci-exact/summary.json) |
| Enforceable PR checks and blocked merge | PASS | GitHub ruleset 27917826 requires six observed Actions contexts on main and has no bypass actors. PR #11 is blocked by failing required checks as well as pending review. Four of six checks passed on tested commit `9126fef`. Sonar CI verified its loopback container and scans a full actual PR checkout per key. Deployment remains on hold. [Rules export](../../tests/team/evidence/phase2/verification/github-main-rules.json) · [Tested commit Actions](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45221445386) · [PR #11](https://github.com/i243086-dotcom/Medihub-SQE/pull/11) |
| Genuine fail-before/fix-after regression | PASS | Same required booking-input job changed from **3 failures, 1 pass** at `34653b0` to **4 passes** at `815b11f`. [Before](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45217711369/job/137843248708) · [After](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45218777165/job/137847005597) |
| Fully green corrected PR and teammate approval | BLOCKED | PR #11 still has unmet API and overall Sonar criteria. Real teammate review remains pending for both PRs. Workflow activation on the default branch awaits authorized merge. |
| Defects, RCA, Pareto, weekly GQM and completion report | PASS | Six confirmed issues, two major evidence-based RCAs, one triaged policy issue, weekly record and residual risk for each risk. Release remains **HOLD**. [Defect, risk and completion review](phase2-defect-and-risk-report.md) |

The public Actions summary captures show the booking job [failing before the fix](../../tests/team/evidence/phase2/verification/ci-before-booking.png), [passing after the fix](../../tests/team/evidence/phase2/verification/ci-after-booking.png), and [all six check outcomes at the tested commit](../../tests/team/evidence/phase2/verification/ci-verified-quality.png). The linked job logs contain the individual test outcomes.

## Tool demonstration and reproduction

Run the following from the existing repository root using the existing Python virtual environment. Use a fresh output folder name per run. The SHA-256 guard checks the development database surrounding every pytest session. Browser assets were downloaded before tests and are checked at run time.

```powershell
$env:MEDIHUB_BROWSER_ASSETS = Join-Path $env:TEMP 'medihub-phase1-browser-assets'
.venv/Scripts/python.exe -B -X utf8 tests/team/tools/run_phase2_verification.py tests/team/evidence/phase2/phase2-viva-run
.venv/Scripts/python.exe -B -X utf8 tests/team/tools/generate_appointment_cases.py tests/team/data/appointments.openapi.yaml tests/team/evidence/phase2/viva-generated.json
.venv/Scripts/python.exe -B -X utf8 tests/team/tools/phase2_mutation.py tests/team/evidence/phase2/phase2-viva-mutation --enforce
.venv/Scripts/python.exe -B -X utf8 tests/team/tools/booking_cfg.py tests/team/evidence/phase2/viva-booking-cfg.md
```

The browser test assets are Vue 3.5.46 and Bootstrap 5.3.0 from the frontend's existing CDNs. Fingerprints are declared in `test_appointment_flows.py`. The available [pytest HTML](../../tests/team/evidence/phase2/verification/release/suite/pytest.html) and [coverage HTML](../../tests/team/evidence/phase2/verification/release/suite/htmlcov/index.html) show the exact complete run. Reproducible tools, final code hashes and fixture controls are in the evidence directory.

Docker Desktop must be running. Use `docker start medihub-sonarqube` when the existing local server has stopped. The instance is bound to loopback on port 9000. Complete SonarQube's first-run password change locally to open the dashboard. Use an analysis token from that instance through the process environment for a rescan.

```powershell
$env:SONAR_HOST_URL = 'http://127.0.0.1:9000'
$secure = Read-Host 'Local Sonar analysis token' -AsSecureString
$env:SONAR_TOKEN = [Net.NetworkCredential]::new('', $secure).Password
.venv/Scripts/pysonar.exe -Dsonar.python.coverage.reportPaths=tests/team/evidence/phase2/verification/release/unit/coverage.xml
Remove-Item Env:SONAR_TOKEN
```

For an optional read-only viva visit to the existing development UI, run Flask from `backend` with `../.venv/Scripts/python.exe -m flask --app app:app run --host 127.0.0.1 --port 5000 --no-reload` if the service is stopped. Avoid submitting changes during this visit. All scoped automated appointment requests use disposable test data and separate test endpoints.

The CI Sonar thresholds require security A, reliability B or better, and at most 3% duplication. The app handles records, so the scan must meet the strict security rating and a reasonable reliability ceiling. The 3% ceiling reflects the published Sonar quality threshold used as the project baseline. Active code remains above the permitted reliability and security ratings. White-box requires 100% statements and branch arcs in scope. Mutation requires at least 75% killed among executed non-error candidates plus both custom mutants killed. This target advances the observed 65% baseline by ten points. The PR must also pass required API and Chromium checks. [Sonar Community Build integration limitations](https://docs.sonarsource.com/sonarqube-community-build/devops-platform-integration/github-integration/introduction)

## Stop boundary

Section 2 has genuine evidence and unresolved release gates. Keep the Phase 2 PR under teammate review. Define the active-slot persistence policy needed to remediate #5 and #12 without losing history. Team ownership and individual hours need confirmation. The usability, defensive security, performance and submission phases remain unstarted in this execution.
