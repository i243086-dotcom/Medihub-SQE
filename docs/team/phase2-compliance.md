# Phase 2 compliance and evidence

**HOLD on 24 November 2026 (PKT).** Tested candidate `ed84dd3cc0b2be87a931222ad210ce38648d1080` ran 723 distinct runtime cases. 369 unit + 324 API + 30 Chromium, with zero failures and skips. The overlapping four-test regression and the Sonar rerun are excluded from the total. [Actions](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45458723990)

## Section 2 verification

| Requirement | Status | Actual result and evidence |
|---|---|---|
| Reconcile Phase 1 and preserve Stage D | PASS | Read-only reconciliation found 67 passed, 12 failed and 15 policy-pending per 94-case snapshot. Stage D commit `256efcb` is an ancestor of the final candidate. Original failed evidence remains. [Raw comparison](../../tests/team/evidence/phase2/phase1_reaudit/run-03-comparison.csv) |
| Test plan, risk register, estimates, traceability | PASS | 10 product and 2 project risks, five exit criteria and a 129.8 person-hour PERT forecast for Section 2. 10/10 original requirements passed scoped candidate acceptance. [Design and criteria](phase2-test-design.md) · [Registry](../../tests/team/test_registry.csv) |
| Human effort and individual ownership | BLOCKED | 1.5 human person-hours recorded. Team must confirm owners and supply actuals. Separately identified tool runtimes are excluded from human totals. [Time log](../../tests/team/evidence/time_log.csv) |
| Sonar real scan, classification and coverage import | PASS | Community Build 26.11.0.134175. 7,308 production lines, 30 backend/frontend source files, 920 cyclomatic and 707 cognitive complexity, 1.1% duplication, 15 smells, 0 bugs, 1 vulnerability, 0 hotspots, 48 minutes debt. A/A/D maintainability, reliability and security. Both runners measured 44.6% combined, 40.7% line and 69.9% branch coverage. [Local scanner](../../tests/team/evidence/phase2/closure/sonar-final/scanner.txt) · [Local measures](../../tests/team/evidence/phase2/closure/sonar-final/measures.json) · [CI measures](../../tests/team/evidence/phase2/closure/final-ci/sonar/evidence/sonar-measures.json) |
| Sonar quality gates | FAIL | The local native gate measured 81.4% new-code coverage against 80%, improved from 68.0%. CI ran on a fresh project with one analysis and evaluated zero native conditions. The overall gate failed in both environments because security D exceeds the unchanged A limit. Reliability A and duplication 1.1% passed. No S4502 disposition was applied. [Technical review](../../tests/team/evidence/phase2/closure/s4502-review.md) · [CI scan](../../tests/team/evidence/phase2/closure/final-ci/sonar/evidence/sonar.txt) · [Working dashboard](http://127.0.0.1:9001/dashboard?id=medihub-phase2-candidate) |
| CFG and function-level comparison | PASS | 91 edges and 69 nodes with one component give 24. Five short-circuit decisions give 29. Counting one conditional expression gives 30, which matches Radon 6.0.1 on `book_appointment`. Sonar measured the whole `patient.py` file at 81 cyclomatic and 97 cognitive complexity. [Numbered CFG](../../tests/team/evidence/phase2/closure/booking-cfg.md) · [Radon reconciliation](../../tests/team/evidence/phase2/closure/cfg-comparison.json) · [Sonar file measures](../../tests/team/evidence/phase2/closure/sonar-final/patient-file.json) |
| White-box, MCC and MC/DC | PASS | 369 unit cases. 720/720 scoped statements and 234/234 branch arcs. All 64 MCC combinations and six independent MC/DC pairs passed. Whole-backend unit plus API coverage was 970/1,170 statements (82.91%) and 260/372 branches (69.89%). [Scoped counts](../../tests/team/evidence/phase2/closure/final-ci/unit/scoped.json) · [Whole-backend data](../../tests/team/evidence/phase2/closure/combined-coverage/coverage.json) · [HTML](../../tests/team/evidence/phase2/closure/final-ci/unit/htmlcov/index.html) · [MCC](../../tests/team/evidence/phase2/closure/final-ci/unit/br02-mcc.csv) · [MC/DC](../../tests/team/evidence/phase2/closure/final-ci/unit/br02-mcdc.csv) |
| Decision tables, transition matrices and boundaries | PASS | BR-01 date/period combinations, patient cancellation matrix, 40 recognized staff transitions and 10 invalid destination checks all passed. The doctor reopening characterization retains allowed free-slot reopening and rejects conflicts. [Decision design](phase2-test-design.md) · [Executed decisions](../../tests/team/evidence/phase2/final-candidate/decision-executions.csv) |
| OpenAPI and generator | PASS | 12 operations and 215 active cases, all passed. 212 exercised JSON validation and three exercised the HTML media type on 405 responses. Corrected previous counts are 205, 202 and three respectively. Applicable signed 64-bit neighboring IDs and seconds-precision admin readbacks passed. The proposed overlay ran separately with 211 passes and four discrepancies. [Active spec](../../tests/team/data/appointments.openapi.yaml) · [Current matrix](../../tests/team/evidence/phase2/closure/api-coverage-matrix.csv) · [Boundary readbacks](../../tests/team/evidence/phase2/closure/boundary-readbacks.csv) · [Proposed output](../../tests/team/evidence/phase2/closure/generated-proposed.xml) |
| API and integration | PASS | 324 API and integration cases include all generated, transport, race and integrity checks. Two race scenarios ran five repetitions each. Each pair returned a 200 and 400 and stored one booking. A new doctor-ID boundary reproduced a 500 before the guard and passed with 404 after it. [Fail-before](../../tests/team/evidence/phase2/closure/doctor-id-before.xml) · [Passing API](../../tests/team/evidence/phase2/closure/final-ci/api/api.xml) |
| Playwright | PASS | 30 Chromium flows across six use cases, with visible outcomes and persistence checks. [HTML](../../tests/team/evidence/phase2/closure/final-ci/browser/browser.html) · [JUnit](../../tests/team/evidence/phase2/closure/final-ci/browser/browser.xml) |
| Cosmic Ray and custom operators | PASS | 514 built-in candidates generated, 391 outside scope, 123 executed, 121 killed (98.37%), two equivalent survivors and zero timeouts or incompetent mutants. Both custom operators killed. [Exact run](../../tests/team/evidence/phase2/closure/mutation-ci-exact/summary.json) · [35 initial survivor reviews](../../tests/team/evidence/phase2/closure/mutation-survivor-review.csv) · [Final equivalent survivors](../../tests/team/evidence/phase2/closure/mutation-final-survivors.csv) |
| Enforceable CI and before/after evidence | PASS | Ruleset 27917826 requires six checks. The previous failing booking run and its corrective rerun remain available. The latest runtime candidate had five green jobs and Sonar red. [Historical booking failure](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45217711369/job/137843248708) · [Booking fix](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45218777165/job/137847005597) · [Six exact jobs](../../tests/team/evidence/phase2/closure/final-ci.json) |
| Fully green corrected PR and approval | FAIL / BLOCKED | Sonar overall fails. Current commit requires genuine teammate review. The reviewers must independently assess the open S4502 evidence before disposition. [PR #11](https://github.com/i243086-dotcom/Medihub-SQE/pull/11) |
| Deployment enforcement demonstration | NOT RUN | The Section 2 wording names both merge and deployment. Actual merge blocking is evidenced. No deployment target exists. Ask the instructor whether merge blocking satisfies this repository's requirement. [Assignment excerpt and evidence](../../tests/team/evidence/phase2/closure/deployment-rubric.md) |
| Defects, RCA, Pareto, GQM and completion | PASS | Six confirmed issues, two major RCAs, 4 validation and 2 integrity defects, weekly GQM and measured exit decisions. 5.77 confirmed defects per scoped KLOC. Reopen rate N/A. Fix verification posted to Issues #5 and #7–#10 and #12, with characterization on #6. All remain open. [Defect report](phase2-defect-and-risk-report.md) · [Final exit review](../../tests/team/evidence/phase2/final-candidate/exit-review.md) |

## Detailed assignment checklist

The 26-item checklist counts the overall failing Sonar gate once. CI merge-block enforcement is demonstrably working. Teammate review is an independent condition of PR delivery in addition to the coursework checklist.

| # | Section 2 item | Status | Evidence |
|---:|---|---|---|
| 1 | Risk-based test plan | PASS | [Design](phase2-test-design.md) |
| 2 | Three-point work estimates | PASS | [Word Section 11](MediHub_SQE_Continuous_Report_Verified.docx) |
| 3 | Original planned milestone calendar | BLOCKED | [Team input required](phase2-test-design.md) |
| 4 | Human effort versus plan | BLOCKED | [Actual time log](../../tests/team/evidence/time_log.csv) |
| 5 | Risk matrix and measurable exits | PASS | [Word Section 12](MediHub_SQE_Continuous_Report_Verified.docx) |
| 6 | Requirements-to-test traceability | PASS | [Registry](../../tests/team/test_registry.csv) |
| 7 | Sonar analysis and measured scope | PASS | [Sonar measures](../../tests/team/evidence/phase2/closure/sonar-final/measures.json) |
| 8 | Sonar quality threshold | FAIL | [Sonar CI](../../tests/team/evidence/phase2/closure/final-ci/sonar/evidence/sonar-measures.json) |
| 9 | Manual CFG and same-function comparison | PASS | [CFG and Radon](../../tests/team/evidence/phase2/closure/cfg-review.md) |
| 10 | Scoped statement and branch coverage | PASS | [Scope totals](../../tests/team/evidence/phase2/closure/final-ci/unit/scoped.json) |
| 11 | 64-case MCC | PASS | [MCC](../../tests/team/evidence/phase2/closure/final-ci/unit/br02-mcc.csv) |
| 12 | Six independent MC/DC pairs | PASS | [MC/DC](../../tests/team/evidence/phase2/closure/final-ci/unit/br02-mcdc.csv) |
| 13 | Multi-condition, transitions and UI boundary design | PASS | [Design](phase2-test-design.md#remediation-verification-on-24-november-2026) |
| 14 | Validated API spec | PASS | [Active OpenAPI](../../tests/team/data/appointments.openapi.yaml) |
| 15 | Own EP and three-point BVA generator | PASS | [Regenerating job](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45458723990/job/138675121933) · [Coverage matrix](../../tests/team/evidence/phase2/closure/api-coverage-matrix.csv) |
| 16 | Two versioned spec-change demonstrations | PASS | [Expected outcome differences](../../tests/team/evidence/phase2/closure/generated-constraint-diff.csv) |
| 17 | Executed API and integration with database readbacks | PASS | [Current API JUnit](../../tests/team/evidence/phase2/closure/final-ci/api/api.xml) |
| 18 | Six use cases and automated flow evidence | PASS | [Chromium HTML](../../tests/team/evidence/phase2/closure/final-ci/browser/browser.html) |
| 19 | Two genuine use-case contributions per member | BLOCKED | [Proposed ownership pending confirmation](phase2-test-design.md) |
| 20 | Cosmic Ray and custom mutations | PASS | [Mutation results](../../tests/team/evidence/phase2/closure/mutation-ci-exact/summary.json) |
| 21 | Analysis of at least 15 actual survivors | PASS | [35 initial survivor reviews](../../tests/team/evidence/phase2/closure/mutation-survivor-review.csv) |
| 22 | Required CI and blocked/corrected evidence | PASS | [Ruleset](https://github.com/i243086-dotcom/Medihub-SQE/rules/27917826) · [Failed run](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45217711369/job/137843248708) · [Correction](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45218777165/job/137847005597) |
| 23 | Deployment block demonstration | NOT RUN | [Rubric reading](../../tests/team/evidence/phase2/closure/deployment-rubric.md) |
| 24 | Defects, two major RCAs and Pareto | PASS | [Defect report](phase2-defect-and-risk-report.md) |
| 25 | Weekly GQM | PASS | [Word Section 16](MediHub_SQE_Continuous_Report_Verified.docx) |
| 26 | Test completion and release assessment | PASS | [Word Section 16](MediHub_SQE_Continuous_Report_Verified.docx) |

**21 PASS, 1 FAIL, 3 BLOCKED, 1 NOT RUN.** The historical records remain available at the earlier checkpoint.

## Evidence and reproduction

The closure [execution count](../../tests/team/evidence/phase2/closure/final-execution-summary.json) and [combined JUnit](../../tests/team/evidence/phase2/closure/final-run/suite/junit.xml) come from the three non-overlapping CI artifacts. The protected development database SHA-256 remained `27be0512bd93cfadb49d7819cff68fe6088334b50b1d2f5a9489d488df6554f5`. Copies only were migrated. [Existing-copy proof](../../tests/team/evidence/phase2/integrity-verify/migration-disposable-copy.json) · [New migration tests](../../tests/team/evidence/phase2/closure/migration/junit.xml)

From the repository root with the existing Python environment and fingerprinted browser assets:

```powershell
$env:MEDIHUB_BROWSER_ASSETS = Join-Path $env:TEMP 'medihub-phase1-browser-assets'
.venv/Scripts/python.exe -B -X utf8 tests/team/tools/run_phase2_verification.py tests/team/evidence/phase2/viva-recheck
.venv/Scripts/python.exe -B -X utf8 tests/team/tools/phase2_mutation.py tests/team/evidence/phase2/viva-mutation --enforce
docker start medihub-phase2-sonar
```

The Sonar candidate lives at [127.0.0.1:9001](http://127.0.0.1:9001/dashboard?id=medihub-phase2-candidate), separate from the existing authenticated project on port 9000. Screenshots of [Issues](../../tests/team/evidence/phase2/final-candidate/sonar/issues-page.png) and [Measures](../../tests/team/evidence/phase2/final-candidate/sonar/measures-page.png) are available with the exports. Use an analysis token through the process environment for rescans.

The only migration command this phase used targeted disposable copies. Before approving application on an existing database, stop writes, take a verified backup, review duplicate active rows, and run `python backend/migrate_appointment_slots.py <offline-copy>` on that copy first. Existing credentials also need rotation before deployment. New secrets should come from the protected environment. The current application has no appointment-duration field, so database conflicts use stored date and start time. A rule for intervals with different starts needs a team-defined duration.

## Pull request disposition

The Stage D test commit and original failed evidence are already included in [PR #11](https://github.com/i243086-dotcom/Medihub-SQE/pull/11). [PR #4](https://github.com/i243086-dotcom/Medihub-SQE/pull/4) remains open. Closing it as superseded requires the user's approval. Neither PR was merged. PR #11 remains blocked and is under teammate review.

The 24-page cumulative [Word report](MediHub_SQE_Continuous_Report_Verified.docx) preserves Phase 1 and records the latest runtime result and remaining gates. [Native pagination and visual QA](../../tests/team/evidence/phase2/closure/word-layout.json)
