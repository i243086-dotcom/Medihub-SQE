# MediHub SQE progress checkpoint

## Phase 4 defensive security — 27 November 2026 (PKT)

Phase 4 used the integrated Phase 3 merge at `436c9ff`. Eight Chromium tests passed through the localhost ZAP proxy, including seven role and ownership decisions plus a transport check. The development SQLite hash and baseline-v0 were preserved. [Evidence index](../../tests/team/evidence/phase4/README.md)

- ZAP 2.17.0 observed 141 messages from the real booking and cancellation workflows. The passive queue drained before 61 alert instances across ten rule IDs were collected. [Session evidence](../../tests/team/evidence/phase4/zap-run.json)
- pip-audit 2.10.1 assessed 99 installed packages and found 103 records across five packages, resolving to 71 advisory groups after alias grouping. [Dependency report](../../tests/team/evidence/phase4/dependency-advisories.html)
- Phase 4 assessment complete. Public release remains on HOLD pending open browser and dependency remediation. [Issue #14](https://github.com/i243086-dotcom/Medihub-SQE/issues/14) · [Issue #15](https://github.com/i243086-dotcom/Medihub-SQE/issues/15) · [Compliance](phase4-compliance.md) · [Word report](MediHub_SQE_Continuous_Report_Verified.docx)

## Phase 3 usability and accessibility — 27 November 2026 (PKT)

Phase 3 branched from the verified application tree on `0b15192` after PR #11 merged. Both required Chromium tests passed before and after the booking-screen correction. All 30 existing Chromium flows passed in the targeted regression suite. The development database digest and original upstream baseline tag were preserved. [Execution and environment](../../tests/team/evidence/phase3/README.md)

- Booking Lighthouse Accessibility improved from 85 to 91. Deduplicated tool findings fell from 19 to 11. Cancellation held at 89 Accessibility with 12 findings. Best Practices measured 100 and SEO 60 for both screens before and after. [Findings](../../tests/team/evidence/phase3/findings.md)
- Real booking now exposes native selection buttons with visible focus, linked form labels and guidance when a slot is taken. The matched report snapshots and all raw outputs are archived. [Checklist](phase3-compliance.md) · [Continuous Word report](MediHub_SQE_Continuous_Report_Verified.docx)
- Phase 3 work and evidence are on `phase3-usability-accessibility`. Phase 4 requires separate authorization.

## Phase 2 release-gate verification

**Technical gates PASS. Production release HOLD.** 36 PASS, 2 PARTIAL and 1 BLOCKED. The 751 runtime passes, full scoped coverage, 64 MCC combinations, six MC/DC pairs and 98.63% mutation were preserved. [Passing workflow](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45663975402)

- The local project verified security A after the owner's exact S4502 disposition. The technical rationale is attached in the local issue comments. The CI process confirmed the same decision against the pinned production files, fingerprint and live technical reviews. The unchanged native gate passed at 88.9% and the overall gate passed at security A. [Local issue history](../../tests/team/evidence/phase2/release-gate/local-sonar-disposition.json) · [CI measures](../../tests/team/evidence/phase2/release-gate/ci-sonar.json)
- The six checks blocked the loopback deployment when Sonar failed and allowed it only after all six passed. [Blocked workflow](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45662563964) · [Successful HTTP and database proof](../../tests/team/evidence/phase2/release-gate/deployment-preview.json)
- Use-case ownership is agreed. The 22–25 November worksheet budgets 96 PROVISIONAL hours, 32 per member. Actual 1.5 setup hours are verified. Confirm actual task dates, hours and contributions, including individual authorship or execution. [Editable plan](../../tests/team/evidence/phase2/release-gate/effort-plan.csv) · [Team evidence](../../tests/team/evidence/phase2/release-gate/ownership-and-effort.md)
- Preserve both open PRs. Production rollout requires owner authorization and review of the existing-data migration. [Word report](MediHub_SQE_Continuous_Report_Verified.docx) · [Full audit](phase2-compliance.md)

## Historical checkpoints

## 25 November 2026 (PKT)

Release **HOLD**. Shaheer and Momin independently supported the S4502 false-positive assessment and formally approved `fde115c`. S4502 remains **Open** at the owner's direction. GitHub requires six checks and one approval. [Live review evidence](../../tests/team/evidence/phase2/independent-closure/github-before.json) | [Dashboard procedure](../../tests/team/evidence/phase2/independent-closure/s4502-disposition.md)

- The candidate scan analyzes its actual base `adf2871`, then the PR merge revision. Sonar verified all 30 production files and measured native new-code coverage of 88.9% against 80%. The overall check failed at security D on S4502. The previous local project measured 81.4% against its separate saved period. [Baseline, scope and gate](../../tests/team/evidence/phase2/independent-closure/ci/sonar/evidence/sonar-measures.json)
- Patient cancellation and both staff update paths returned three HTTP 500s above the SQLite integer limit before the fix. The focused regression passed all 53 checks after the fix. A later targeted regression killed the previously surviving cancellation range mutant in an isolated copy. [Before](../../tests/team/evidence/phase2/independent-closure/appointment-id-before.xml) | [After](../../tests/team/evidence/phase2/independent-closure/candidate-regression.xml) | [Exact mutant](../../tests/team/evidence/phase2/independent-closure/overflow-observation-mutated.txt)
- GitHub reports no deployment environments or deployment history. Team dates, human hours and individual use-case authorship require confirmation. PR #11 remains open and blocked. PR #4 remains open as superseded discovery evidence. [Run on the boundary fix](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45651014316)

Final executed source candidate `0d175f4` passed **751 distinct cases**. The counts were 385 unit, 336 API (227 generated), and 30 Chromium. The scoped gate passed 720/720 statements, 234/234 branch arcs, 64 MCC and six MC/DC pairs. Mutation killed 144/146 built-in mutants (98.63%) and both custom operators. The new targeted case killed the former cancellation limit survivor. [Source workflow](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45653206386)

The edited continuous Word report in this directory has 26 pages and retains Phase 1. Section 11 has 130 PROVISIONAL planned hours distributed as Syed 48, Shaheer 39 and Momin 43. Only Syed's 1.5 setup hours are recorded as actual. The Section 2 audit has **34 PASS, 1 PARTIAL, 1 FAIL and 3 BLOCKED**. [Complete audit with Word and evidence references](phase2-compliance.md)

## Previous verified checkpoint

**24 November 2026 (PKT). Phase 2 verification update. Release HOLD.**

- Tested candidate `ed84dd3cc0b2be87a931222ad210ce38648d1080`, team branch `phase2-verification`. The full applicable suite ran 723 distinct passes, zero failures and zero skips. Unit 369, API 324, and Chromium 30. The 215 active OpenAPI cases passed, with 212 JSON schema validations and three HTML media-type checks. Four proposed-contract diagnostic cases failed separately.
- The appointment scope passed 720/720 statements and 234/234 branch arcs. All 64 MCC combinations and six MC/DC pairs passed. Numbered booking CFG M=24, or 29 with short-circuit operands. Counting the inline conditional expression gives 30, matching Radon 6.0.1. Sonar's 81 is the `patient.py` file total.
- Issues #5 and #12 passed after enforcing active SQLite doctor and patient start-time uniqueness. Cancelled rows and treatment references were retained. Ten coordinated concurrency scenarios passed with one HTTP 200, one HTTP 400 and one booked row per pair. Validation fixes #7 to #10 passed their regressions. #6 was characterized from the implemented rules.
- The protected development database hash is still `27be0512bd93cfadb49d7819cff68fe6088334b50b1d2f5a9489d488df6554f5`. The migration passed on a disposable copy. SMTP was blocked.
- Full-scope Sonar measured 7,308 production lines, 44.6% combined coverage, 0 bugs and 1 vulnerability. Reliability and maintainability A. Security D on open S4502. The local native gate passed at 81.4% new-code coverage against 80%, up from 68.0%. The disposable CI project has only one analysis and evaluated no native conditions. The required overall security gate failed locally and in CI. All 26 transport checks passed, including the 14 protected write routes. [Dashboard](http://127.0.0.1:9001/dashboard?id=medihub-phase2-candidate) · [Independent review request evidence](../../tests/team/evidence/phase2/closure/s4502-review.md)
- Final Cosmic Ray evidence killed 121/123 built-in mutants, 98.37%, and both custom mutants. The ledger has 35 genuine initial survivor analyses and both final equivalent survivors.
- Required checks passed 5/6 on the tested commit. Review remains requested of both teammates. PR #4 is inherited by PR #11 and remains open as historical discovery. [Actions](https://github.com/i243086-dotcom/Medihub-SQE/actions/runs/45458723990) · [PR #4](https://github.com/i243086-dotcom/Medihub-SQE/pull/4) · [PR #11](https://github.com/i243086-dotcom/Medihub-SQE/pull/11)
- The Section 2 checklist has 21 PASS, 1 FAIL, 3 BLOCKED and 1 NOT RUN. The new signed-ID availability regression verified the fix for a 500. Native Word counted 24 pages in the updated continuous report. [Runtime count](../../tests/team/evidence/phase2/closure/final-execution-summary.json) · [Word layout](../../tests/team/evidence/phase2/closure/word-layout.json)

The [compliance matrix](phase2-compliance.md), [test plan](phase2-test-design.md), [defect record](phase2-defect-and-risk-report.md) and [cumulative report](MediHub_SQE_Continuous_Report_Verified.docx) point to reproducible evidence. The [November 23 audit](progress/2026-11-23-phase1-runtime-and-stage-d.md), baseline tag `e58ce85` and original Stage D evidence are preserved.

## Outstanding at the previous checkpoint

1. Obtain independent technical disposition of S4502, carry the approved disposition into the required CI scanner and rerun the unchanged overall gate.
2. Supply the original planned dates and actual human time by work area. Each teammate must confirm use-case authorship and review the PR under their own account. The [test design](phase2-test-design.md) lists the exact records.
3. Ask the instructor whether enforceable PR merge blocking meets the deployment criterion for an undeployed MIS. Deployment blocking has no execution evidence.
4. Approve merge and migration rollout only after the required checks and reviews. PR #4 requires separate approval to close as superseded. Phase 2 remains on HOLD.
