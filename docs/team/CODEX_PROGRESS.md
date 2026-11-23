# MediHub SQE progress checkpoint

**23 November 2026 (PKT). Phase 2 was authorized and executed. Release is on HOLD. Work stops at the Phase 2 boundary.**

## Phase 2 checkpoint

- [Section 2 compliance matrix](phase2-compliance.md) records each rubric item and its evidence. [Test design and use cases](phase2-test-design.md) and [defect, risk and completion review](phase2-defect-and-risk-report.md) contain the supporting plans and controls.
- Tested application and test code at commit `9126fef`. The final local suite recorded 560 distinct executions with 556 passed and four failed. The 312-unit subset measured 703/703 statements and 226/226 branch arcs in the appointment scope. All 64 MCC cases, six MC/DC pairs, 196 active generated API cases and 30 Chromium flows passed. [Execution and coverage](../../tests/team/evidence/phase2/verification/release/suite/pytest.html)
- The four remaining failures cover rebooking under #5, two concurrency variants under #12 and the historical provisional doctor transition assertion under #6. Unknown admin statuses and malformed booking inputs have retested fix candidates in PR #11. They remain open pending review. The development database hash stayed unchanged. [JUnit](../../tests/team/evidence/phase2/verification/release/suite/junit.xml)
- SonarQube ran locally on port 9000 and in GitHub Actions. The final local scan imported coverage and measured 41.0% project coverage, complexity 904, reliability C and security E. Security and reliability exceed the permitted limits. [Sonar evidence](../../tests/team/evidence/phase2/verification/sonar-release-thresholds.json)
- Main ruleset 27917826 requires six observed checks and has no bypass actors. The tested commit passed the booking regression, white-box, Chromium and mutation jobs. API and Sonar blocked it. PRs #4 and #11 still await genuine review. [Tested commit Actions](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45221445386) · [PR #11](https://github.com/i243086-dotcom/Medihub-SQE/pull/11)
- Mutation analysis ran locally and in CI, killed both custom candidates, and reviewed 35 real initial survivors with improved assertions. The tested commit measured 116 killed of 118 executed built-in candidates, or 98.31%. [Mutation results](../../tests/team/evidence/phase2/verification/mutation-ci-exact/summary.json)
- The [cumulative Word report](MediHub_SQE_Continuous_Report_Verified.docx) contains measured Section 2 results and remains in the existing local repository.

## Verified audit

| Scope | Result | Evidence |
|---|---|---|
| Assignment and source | Reviewed the seven-page rubric, supplied scope/report/guide/history, annotated baseline, current backend and Vue, SQLite schema, and existing QA work. | [Initial reconciliation](progress/2026-11-23-initial-audit.md) |
| Phase 1 | Tagged `e58ce85` and current `256efcb` each ran 93 HTTP cases and one Chromium workflow on port 5001. Per build, 67 passed, 12 failed and 15 recorded behavior pending policy. The verdicts matched across revisions. | [FR/BR and hypothesis matrix](progress/2026-11-23-phase1-runtime-and-stage-d.md), [baseline result](../../tests/team/evidence/phase2/phase1_reaudit/run-03/baseline.json), [current result](../../tests/team/evidence/phase2/phase1_reaudit/run-03/current.json), [environment](../../tests/team/evidence/phase2/phase1_reaudit/run-03/environment.json) |
| Stage D | Fresh unchanged pytest suite ran 12 cases with 6 passes and 6 failures. Smoke selection ran 9 cases with 3 passes and 6 failures. These suites overlap. The SMTP guard passed. | [Full log](../../tests/team/evidence/phase2/phase1_reaudit/stage-d-full.log), [smoke log](../../tests/team/evidence/phase2/phase1_reaudit/stage-d-smoke.log), [hashes and commands](../../tests/team/evidence/phase2/phase1_reaudit/stage-d-environment.txt) |
| Test registry | 12 existing pytest nodes and 94 distinct Phase 1 audit cases, with evidence and relevant Issue links. Reproduction variants intentionally overlap at the behavior level. Do not add rerun counts or infer full requirement coverage from registry size. | [Registry](../../tests/team/test_registry.csv) |
| Isolation | Original development SQLite SHA-256 matched before and after. The HTTP and Chromium runs used disposable file-backed databases and recorded zero SMTP attempts. The development UI on port 5000 was unavailable. | [Run environment](../../tests/team/evidence/phase2/phase1_reaudit/run-03/environment.json) |
| Cumulative report | Updated the Phase 1 findings, traceability, Stage D and AI-use entry in the local editable report. Preserved the supplied document and a versioned backup in the excluded inputs folder. Exported through Word to a 15-page QA PDF and inspected the cover, page breaks and tables. | [Cumulative Word report](MediHub_SQE_Continuous_Report_Verified.docx) |

## Audited starting repository and open decisions

- The user independently reviewed the Phase 1 and Stages A–D audit. The audit is committed at `ccafb97` and included in Phase 2 PR #11. Phase 1 evidence remains in `53e8dd9`. `baseline-v0` still resolves to `e58ce85`.
- Team `main` is `adf2871`. Stage branches are `phase2-setup` (`bc3cdfc`), `phase2-tools` (`968ca63`), `phase2-testdb` (`9c708fc`) and `phase2-smoke` (`256efcb`). PRs #1–#3 merged. The initial audit records the separate `origin` and `upstream` remotes.
- [PR #4](https://github.com/i243086-dotcom/Medihub-SQE/pull/4) remains open. The authorized description correction and requests for Shaheer and Momin were recorded. The audit observed review protection and zero PR checks. A genuine teammate review and a team decision on where to keep the discovery evidence remain pending.
- Open Issues [#5](https://github.com/i243086-dotcom/Medihub-SQE/issues/5) and [#7](https://github.com/i243086-dotcom/Medihub-SQE/issues/7)–[#10](https://github.com/i243086-dotcom/Medihub-SQE/issues/10) reproduced as five confirmed defects. [#6](https://github.com/i243086-dotcom/Medihub-SQE/issues/6) remains triaged pending doctor transition policy. Confirm the intended exact-hour API rule and the intended handling of past-date slot discovery before changing policy.
- At the audit checkpoint, concurrent writes, complete MCC, admin rescheduling and doctor-list date boundaries still needed coverage. The Phase 2 evidence above records the subsequent executions. Passive runtime security verification belongs to Phase 4. No supplied definition for H-06 was located. The assignment registration is reported by the team and remains independently unverified.

## Remaining decisions and stop boundary

1. Keep the integrity and Sonar failures visible. Resolve the active-slot schema/migration policy and the role-specific transition and slot-listing policies before remediation.
2. Have genuine teammates review PRs #4 and #11 and confirm work ownership and actual effort. Obtain authorization before any merge. The resolved count and reopen-rate denominator remain zero.
3. Complete SonarQube's locally prompted first-run password change in the UI to demonstrate the dashboard. The metric exports are available immediately.
4. Do not begin Phase 3 until the user explicitly says **Continue Phase 3**. Sections 3–6 remain outside this run.
