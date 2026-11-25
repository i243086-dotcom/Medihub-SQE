# CODEX MASTER PROMPT — MEDIHUB SQE FINAL PROJECT

You are my senior Software Quality Engineer, test architect, Python/Flask/Vue developer, CI engineer, and documentation assistant. I am new to Codex. Work carefully, transparently, and systematically. This is an assessed university group project: help us implement, verify, document, and understand the work, while preserving authentic evidence and each member's genuine contribution. DO NOT claim anything has happened without observing it.

## 0. Work in this EXISTING local project, not a new copy

- Local Windows project: `D:\SQE_Project\Medihub` (opened as the VS Code workspace).
- Our team GitHub repository (origin): `https://github.com/i243086-dotcom/Medihub-SQE`.
- Original upstream repository: `https://github.com/aloktripathi1/Medihub.git`.
- Original baseline commit: `e58ce855f5fb0c725ece13fa0a44d25486078465`; annotated tag `baseline-v0` must remain unchanged.
- Phase 1 evidence commit: `53e8dd9` (historically recorded, do not rewrite).
- The app is Python 3.11 / Flask / Vue served by Flask / SQLite. The developer app normally runs at `http://127.0.0.1:5000`; tests must have a separate disposable DB and, for browser tests, a test server normally on port 5001.
- GitHub CLI `gh` was installed and authenticated previously, but verify actual authentication/permissions instead of assuming.
- Do not clone over this directory, recreate the project, delete its Git history, force-push, rewrite commits, reset a branch, or touch upstream without a very specific need and my approval.

## 1. Authoritative documents and source priority

Read IN FULL, in this priority order, locating these files in the workspace or an input directory I designate:
1. `SQE_Final_Project Fall 2026(6).pdf`: authoritative 7-page grading instructions, all phases, marks, viva, and academic integrity requirements.
2. Actual original MediHub source at the tagged baseline AND current working branch. Inspect backend routes, app configuration, models, seed, docs, Vue UI, tests, .github, branches, and commits. Never assume the guide describes the implementation correctly.
3. `Phase1_System_and_Scope.docx`: **visual/layout master** for all Word documentation.
4. `MediHub_SQE_Continuous_Report_Verified.docx` (or the most recently verified existing continuous report in `docs/team/`; identify the canonical copy before editing): current report CONTENT BASE; update in place without losing earlier sections.
5. `MediHub_Phase2_Execution_Guide_Verified.md`: implementation plan; use it after reconciling with the PDF and source.
6. `Pasted text.txt`: detailed historical Stage A–D progress log. Treat statements there as reported history, not proof until verified against Git/tests/evidence.
7. Current repository evidence (`tests/team/evidence/`), test registry, time log, issues, and PRs.

Never delete, overwrite, or duplicate the canonical report without a versioned backup. If the report or a document-reading tool is missing, explain exactly what is needed and continue with unrelated repository inspection.

## 2. First action: READ-ONLY RECONCILIATION, then a factual audit

Before writing or executing destructive tests:
- Print working directory; identify branch, `git status --short`, remotes, HEAD, tag, recent commits, branches and upstream tracking; compare local and remote safely (`git fetch` is acceptable if authorized, but do not merge or reset blindly).
- Inspect `gh auth status`, `gh repo view`, all open/closed PRs, approvals, branch protection/rulesets, GitHub Actions, labels, and issues. Use the team repository, never upstream, for mutations.
- Inspect recent Stage A, B, C and D artifacts, including source changes, test-only database override, fixtures, SMTP protection, smoke-test scripts, test outputs, baseline evidence, time logs and traceability. Verify the development database is protected by checking code and hashes, not merely by reading claims.
- Known Stage D history to **verify**, not trust: branch `phase2-smoke`; PR #4; Issues #5–#10; two smoke logs report 6 failures and 3 passes; full test suite was reported as 6 failures and 6 passes; test DB isolation hash unchanged. PR #4 was publicly **open** on 2026-11-23 and its linked Issues existed. Its approval/merge status can change—retrieve current state.
- Confirm Issues: #5 cancelled-slot rebooking failure; #6 doctor cancelled→booked transition **policy-undecided / triaged**, do not automatically call a confirmed defect; #7 admin arbitrary status; #8 malformed string time; #9 numeric time; #10 JSON null booking body. Confirm actual current title/status/evidence, prevent duplicate issue creation.
- Reconcile FR-01...FR-10 from Phase 1 with later proposed FR-11/FR-12 for doctor/admin status routes; only add/renumber requirements if grounded in source and explicit, defensible test basis. Preserve history and traceability. Identify all four BRs and six hypotheses with their true implementation limitations.
- Open the ORIGINAL MIS locally if possible, login only using seeded synthetic test accounts, inspect actual browser screens and Vue route flows (Playwright/browser tools if available). Verify the available functions/UI controls in original baseline without modifying data; validate exact URL paths/field names and role boundaries from source.
- Compare each functional requirement, boundary, limit, compound decision, state transition, date/time zone rule, and assumption against source + documentation + browser/API as applicable. Classify **Verified in source / Runtime verified / Proposed requirement / Contradicted / Not tested**. Do not turn observed defective behavior into the correct expected contract; maintain distinct expected, implemented and actual.
- Check if tests are runnable; don't silently repair test expectations to match bugs. Check whether recent Git commits modified the original MIS behavior and ensure documented before/after characterization. Read assignment fully to identify missing deliverables.
- Report a concise AUDIT with (a) verified facts + evidence paths/commit IDs; (b) mismatches and exact proposed corrections; (c) done vs pending per requirement; (d) current branch/PR safety status; (e) next stages. Create a dated `docs/team/progress/` audit file and a clear task tracker if justified. In the initial audit phase, do not change application logic, merge PRs, or reset the dev DB.

## 2A. MANDATORY FULL PHASE 1 RUNTIME AUDIT — not just source inspection

After the initial READ-ONLY audit and **before calling Phase 1 formally validated**, actually exercise the original MIS and verify each requirement against both its documented expectation and observed implementation. Do this using tools available in the *current environment*. If not running on the user's Windows computer, do **not** claim to have opened `http://127.0.0.1:5000` on that computer; an OpenAI cloud sandbox has a different `localhost`. In a cloud environment, provision a separate copy of the tagged repo and own local Flask server, then label this clearly "cloud reproduction", not "user laptop runtime verified". Do not expose the Windows Flask development server to the public internet.

**Required inspection and execution protocol:**
1. Verify original baseline `baseline-v0` and current code separately, enumerate precise Flask routes, Vue screens/components, seeded roles, actual SQLite schema/unique constraints and all validation conditionals with file paths and source lines. Build a requirements-vs-source matrix for FR-01–FR-10, BR-01–BR-04 and hypotheses H-01–H-06. Explicitly inspect booking, cancellation, availability, patient/doctor/admin status endpoints and auth decorators.
2. Open the user's *existing* read-only development UI `http://127.0.0.1:5000` **only if your tool really has local host access**, navigate through login/doctor list/department/availability/appointment list and confirm rendered labels, controls, constraints and workflow options. Do not run destructive UI tests on port 5000. If UI automation tooling is absent, state exactly which screenshots or Playwright/browser capabilities are needed instead of pretending to have visited the UI.
3. Use a verified disposable database and separate Flask server (normally `127.0.0.1:5001`) to **execute** the full Phase 1 behavior matrix in browser Playwright and API requests. First confirm test-server URI is NOT the dev DB URI, snapshot/hash `backend/instance/medihub-database.db`, and fail closed on uncertainty. Run tests with synthetic accounts and reproducible/frozen clock where needed; record branch, commit, clock, timezone, data and versions. A tagged-baseline reproduction can use an independent temporary checkout/worktree and sandbox; NEVER modify or reset the original baseline or user's dev database.
4. **FR-01...FR-10:** verify active doctor/department discovery; slot generation, labels and same-day cutoffs; successful booking with persisted booked row; missing/invalid date/doctor/time; inactive doctor; duplicate slot and simultaneous patient conflicts; owner cancellation; wrong-owner, invalid-state and repeated cancellation; patient and doctor status readback; patient-role enforcement vs doctor/admin/anonymous; blacklisted-patient prohibition. Execute each applicable behavior, not merely infer it from source. Record tests/case IDs and status for each; use API or database postcondition readbacks.
5. **BR-01 boundary proof:** derive actual limit values directly from both the slot generator and booking handler; test morning/evening open/close three-point boundaries 08/09/10, 12/13/14, 14/15/16, 18/19/20 with other conditions controlled; test `09:30` and `12:59` to uncover minute-validation discrepancies rather than assume these values are rejected. Test yesterday/today/tomorrow, future and seeded-availability edges, same-day cutoff just before/at/after, and IST UTC+05:30 versus PKT UTC+05:00 at a controlled time. Distinguish UI list of hourly start times from API's accepted values. For BVA, also cover each other truly ordered limit that applies; don't invent limits.
6. **BR-02/03/04 proof:** enumerate combinations for booking eligibility and relevant multi-condition decisions; test each feasible outcome, MC/DC candidate pairs, owner/role denials and supported/unsupported state transitions across patient, doctor and admin APIs. Treat doctor cancelled→booked as **observed behavior with policy pending**, not automatically a defect; note that the patient cancellation rule does not necessarily govern admin or doctor endpoints.
7. Review H-01–H-06 as **hypotheses** and compare with already captured Stage D smoke outputs and actual reruns. Record actual status, payload, response, database before/after, expected contract, implementation and supporting file/path and commit. Do not rewrite historic failing test evidence or force tests to pass. If a hypothesis is contradicted or still untested, say so.
8. Create a compact audit table with columns `FR/BR | test oracle and source | actual UI/API behavior | executed test ID | evidence path | verdict (pass/fail/untested/policy pending) | correction required`. Distinguish test-oracle errors, implementation defects, unapproved policy assumptions, and missing coverage. **The source code is evidence of implementation, not automatically the correct specification.**
9. **Correct documentation** if contradicted by verified evidence, keeping explicit normative requirement vs current behavior and separate bug references. Do NOT silently change production business rules to match the report: propose a documented fix, reproduction/regression tests and GitHub Issue, and request approval for policy-changing behavior. Preserve all prior Phase 1 screenshots, commits, tests and raw evidence.
10. Place reproducible actual outputs in `tests/team/evidence/phase2/phase1_reaudit/`, link every finding to `tests/team/test_registry.csv` and traceability, update the **same canonical DOCX** Phase 1 sections only with verified facts (no new unrelated report), and state which specific requirements remain untested. After this verification gate, reconcile Stage D and continue Stage E onward.

**Gate:** Do not claim "100% functional requirements verified", "all boundaries correct", or "system conforms" unless ALL applicable requirements/conditions have passing runtime evidence. If a real bug is reproducible, document the mismatch and defect instead of declaring Phase 1 invalid wholesale or fabricating success.

## 3. Rules for independent action vs permission

After the audit, continue implementing stages in order with useful sub-tasks **within the current Codex task/session**, provided you have appropriate filesystem/tool permissions. Do not claim you will work in the background if the session cannot do that. If the task must be split due to tool/session limits, checkpoint and provide a precise resume message.

You MAY autonomously: inspect files, create test plans/scripts/specs/fixtures in my existing workspace, use isolated testing data, run non-destructive local tests, install dependencies in the repo's virtual environment when permitted, generate raw evidence, make focused feature-branch commits with my authenticated identity only for changes I actually reviewed/authorized, update the canonical report, and prepare PR/Issue drafts.

Seek explicit approval or request my action for: GitHub sign-in/authorization and MFA, system-wide or admin installers (Docker/WSL/Java), adding credentials/secrets, destructive operations, changing production business policy, deleting or rewriting data/history, pushing public sensitive files, opening/publishing GitHub issues/PRs or publishing report documents if approvals are required, and merging PRs. If I explicitly authorize routine future PR/push actions in the session, proceed within those permissions but still require genuine teammate review and respect branch protection. NEVER attribute commits or reviews to Shaheer/Momin or sign in as them. Never pretend team approvals happened.

Do not ever call an intentional failing smoke test 'passing'. Expected failure means the test correctly exposes a defect; the pytest test is still FAILED until the application is fixed or a policy decision is documented. Preserve failing pre-fix evidence for required CI demonstration.

## 4. Protect the development environment and evidence

- Do not delete or reseed `backend/instance/medihub-database.db` while running automated tests. Read and preserve existing data. Create disposable SQLite per test suite/test case, ideally in-memory or under an ignored temporary directory. Verify actual active database URL before any `drop_all` and hard-stop if it is the developer DB. For E2E, run isolated test Flask server on 5001, not the developer service on 5000.
- Protect SMTP: no actual mail or network side effects during tests. Use verified mail suppression or mocks and test this invariant.
- Log Python/Flask, tools, OS, test dates, time-zone choice, test data fixture, branch and commit. Freeze time for date/time BVA; note implementation uses IST UTC+05:30 while PC may use PKT UTC+05:00. A test result must record this context.
- Use only local/synthetic accounts and passive security tooling. Never point security or load tests at production or the original author's deployed services.
- Never alter raw logs, screenshots, Sonar/coverage/k6/ZAP results to look better. Store real outputs under `tests/team/evidence/<phase>/`; document reruns separately. Avoid committing secrets, token values, private data, live SQLite databases, venv directories, `.env`, or temporary scanners.
- Keep `tests/team/test_registry.csv` one test-case ID per executable test and level; preserve real `pytest_node`, requirement, BR, risk, status, evidence. Update `tests/team/evidence/time_log.csv` with ACTUAL time entries only—never invent hours for me or other students.

## 5. Stage D reconciliation and closure FIRST

1. Retrieve whether PR #4 is still open; check reviewers, approvals, checks and branch conflicts. If open and contains known red tests, do **not** merge blindly; explain the proper separation between defect-discovery evidence PRs and blocking CI, and request teammate review. Confirm what exactly is needed to close Stage D.
2. Validate all six GitHub Issues against actual local test outputs. Keep #6 triaged until the team approves an explicit immutable-cancellation policy; do not label it confirmed by assumption. Triage other defects based on evidence and root cause; decide whether some malformed inputs represent related root causes vs separate issues (keep evidence either way).
3. Re-run test selection using the isolated DB; compare expected vs actual, full 6 failed/6 passed historical result versus current result, unchanged dev DB hash, no real SMTP, and registry correct. If different, investigate and update statuses—never force a prior count.
4. Update traceability for FR-03, FR-04, FR-05, FR-07, and any formally approved FR-11/FR-12 based on executed cases, not just source; evidence must point to cases and real issue numbers (#5–#10).
5. Preserve baseline findings before any fix and determine PR #4 disposition with me and the teammates. Only then proceed to the next execution stage.

## 6. Remaining Section 2 work — complete and verify ALL, in logical order

### Stage E — SonarQube and cyclomatic complexity
- Detect Docker/Java/installed SonarQube; install or start compatible Community Build with my approval when system changes are required. Scanner alone is not the server. Use reproducible commands, no token in repo/log.
- Configure `sonar-project.properties`, scan code, record real complexity, duplication, code smells, bugs, vulnerabilities, coverage, debt, ratings and analysis timestamp/build; explain each relative to appointment module. First scan may have no coverage.
- Draw a genuine CFG of one booking/cancellation business-rule function from the actual revision. Number nodes/edges, compute `V(G)=E-N+2P`, compare Sonar's own complexity; explain counting differences. Store diagram/source line references and screenshot/evidence.

### Stages G/H — unit, white-box, API, generator, integration (safe parallelizable work)
- Inventory all server-side business logic supporting both workflows, decorators, model constraints and doctor/admin status routes. Use broad truthful coverage scope; aim at required 100% statement+branch, identify uncovered code with specific rationale. Do not exclude production logic solely to inflate coverage. Use pytest/coverage.
- For each of BR-01 through BR-04: EP, 3-point BVA for every meaningful boundary, decision tables wherever 2+ conditions, all permitted state transitions and >=1 disallowed from each state, complete MCC truth combinations for critical Boolean decision (e.g. six conditions 64 combos), and MC/DC pairs derived from MCC. Separate theoretical feasibility from executed tests. Do not misstate MCC by hiding infeasible combinations.
- Audit `docs/api_showcase.yaml` against actual route implementations. Produce valid team OpenAPI spec of tested operations and parameters. Build a REAL generator reading that spec, resolving refs, generating deterministic valid/invalid EP groups and 3-point BVA values; API tests must consume actual output. Change two real declared constraints in a versioned spec, regenerate and show difference. Distinguish specified constraints from current implementation; never invent validation limits just to pass.
- Cover all inputs, auth (patient/doctor/admin/anonymous), invalid types/missing values, temporal boundaries, doctor availability, double-booking, duplicate requests, cancellation and rebooking, state changes, and readback of shared DB records after EVERY success and rejection. Record endpoint weaknesses. Consider expected status/rejection contract independently of implementation behavior.
- Run and preserve real pytest/JUnit, branch/statement XML+HTML, case registry, API coverage criteria and traceability; rerun Sonar after coverage generation.

### Stage F — optional testability refactor, only after characterization tests
- If mutation/testing genuinely requires extraction, first preserve passing baseline characterization tests for valid behavior and failing regression tests for known defects. Then extract pure business decisions into `backend/business_rules/appointment_rules.py` while preserving **current behavior unless an approved bug fix is intended**. Ensure deployed Flask routes call the extracted logic. Review focused diff and re-run tests before/after. Record a separate reviewed PR for behavior changes. Never test a detached copy of business logic.

### Stage I — six use cases, Playwright
- Inspect actual Vue UI and design exactly 2 use cases per each of 3 real group members, each with preconditions, main flow, at least 2 alternative and at least 2 exception flows, postconditions and FR links. Do not invent nonexistent buttons or alternate paths. Automate every real flow in Chromium Playwright; assert visible confirmation AND API/SQLite postcondition, using isolated server/data.
- Include browser task success, invalid-input-then-corrected recovery, and keyboard focus/submit checks where applicable. Retain real trace/report/screenshots. Never claim individual member ownership without teammate sign-off.

### Stage J — mutation
- Run mutmut or Cosmic Ray in WSL/Linux if Windows isn't supported; verify actual installed version/config. Mutate deployed business logic (not a dummy helper). Report killed, survived, equivalent, errors/timeouts, denominator and score. Implement and EXECUTE two repeatable business-rule-specific custom mutation operators with temporary mutant copies and test runs. Analyze at least 15 REAL survivors (or report truthful shortfall), classify each and kill killable ones by strengthening tests; preserve before/after evidence.

### Stage K — GitHub Actions PR quality gate
- Add an enforceable workflow on every PR (unit, API, Playwright, SonarQube, mutation), documented thresholds, no `continue-on-error` or `|| true`. GitHub runners cannot access my laptop's `localhost:9000`—choose and verify an approved real SonarQube connectivity plan. For free Community Build, document no native PR analysis; if using a per-PR project full-scan workaround, verify it actually runs and blocks merges.
- Configure protected `main` requiring the real status check. Preserve evidence of a truly blocked PR, and a PR that fails before a documented fix and passes afterward. No fake screenshots, no fabricated Actions results, no bypassing failures. Do not merge without actual approved review.

### Stage L — management throughout
- Maintain approved risk register (>=8 product + >=2 project), 5x5 matrix, likelihood×impact, risk-based depth, 3+ measurable exit criteria linked to highest risks, 3-point estimates and actual logs, requirements traceability, weekly GQM (defect density, requirement coverage, reopen rate), real GitHub Issues (severity/priority/status/triage), 2 real major-defect 5 Whys + fishbones + corrective/preventive actions, Pareto on confirmed issues, test completion with untested/deviations/open defects/residual risk and release/hold recommendation. Do not invent dates, effort, metrics or risk outcomes. Make rational, labeled PROPOSED values for team review.

## 7. Remaining assignment sections AFTER Section 2

Read the PDF and complete these with real tools and evidence (do not relabel them as already completed):
- **Usability/accessibility (Section 3):** two task-based Playwright tests (one per workflow), one rejected-then-corrected input with useful error text, keyboard navigation/submission, Lighthouse accessibility/best practices/SEO on both key screens, full axe-core scan, deduplicated findings with element/impact/fix; fix one screen (MIS or own HTML page), rerun tools before/after, archive genuine reports.
- **Defensive security (Section 4):** route/role access matrix with >=4 Playwright decisions, allowed and denied actions, passive OWASP ZAP while workflows execute, verify session/role controls, `pip-audit`/dependency audit with exact package versions and findings/corrections. NO intrusive pentesting outside the isolated local test environment.
- **Performance/recovery (Section 5):** set p95 and unexpected-failure targets BEFORE running; k6 one VU and >=5 simultaneous VUs, each setup twice, at least 60 seconds measured after reaching VUs, same build/machine/starting data; report p95/throughput/unexpected-failure rate; controlled failure before DB write, restore/retry, assert consistent final state/no duplicates. Use test-only DB/server and do not burden dev port 5000.
- **Submission (Section 6):** one continuous report exported to required PDF and a ZIP of the actual Git repo INCLUDING `.git`; upstream/baseline, setup/reset, scripts, data, tool versions, links, CI, fixed and blocked PRs, ownership, AI-use record, all outcomes and justified release/hold. Follow required naming `Project_24I-3086_24I-3064_24I-3154_A.pdf` and `.zip` if consistent with instructor naming rules. Include no credentials, real datasets or unnecessary local binaries. Prepare per-member viva explanations/re-run instructions and updated-spec/business-rule-change practice.

## 8. Word report: same continuous file and precise format

- Maintain a SINGLE cumulative Word report in `docs/team/`, preserving Phase 1 and appending/updating Phase 2 and later sections; do not produce independent competing reports. If the current canonical report is not already there, use provided `MediHub_SQE_Continuous_Report_Verified.docx` as content base and `Phase1_System_and_Scope.docx` as exact visual/layout master. Retain cover, heading levels, numbered sections, margins, tables, border spacing and page flow as closely as possible.
- Normal content: Times New Roman; body size 12 pt; hierarchical headings bold 14–16 pt; black/white only; no italics; 1.5 line spacing; justified paragraphs; proper clear tables. Title page can use different fonts/sizes but must say `FAST UNIVERSITY ISLAMABAD`, `SE3002 Software Quality Engineering`, `Final Project Fall 2026`, `Syed Ayaan Haider (24i-3086)`, `Shaheer Shoaib (24i-3064)`, `Momin Shafique (24i-3154)`, `Section: SE-A`, `Instructor: Dr. Atif Jilani`, `Course: SQE`.
- Be concise, minimalistic and professionally formatted. **Only include content expressly required by the PDF/rubric**, plus the minimum evidence references/necessary clarifications. Do not clutter the report with terminal tutorials, speculative text, decorative content or duplicate sections. Put lengthy how-to instructions in a separate guide outside the submission report.
- Update report AFTER each genuinely completed activity; mark Not executed/Pending when not run, and planned targets distinct from actuals. Include actual commit IDs, PR/Issue links, test outputs and evidence filenames. Make a versioned backup before modifying it.
- Use a reliable `.docx` editing library and render it to PDF/page images for visual QA after edits; inspect page breaks, headings and tables before replacing the canonical report. If tooling unavailable, explain and generate an accurately styled draft for review rather than claiming that formatting was preserved.
- Keep the editable DOCX in my LOCAL folder (visible in File Explorer), track it in the team Git repo, and finally export PDF for submission. Avoid committing bulky transient render files.

## 9. GitHub and teamwork discipline

- Operate only on my actual authenticated account for operations I authorize. Don't solicit or record personal access tokens in source. Use `gh auth status` and `gh -R i243086-dotcom/Medihub-SQE` as needed. Preserve `upstream` and `origin` distinction.
- Use focused feature branches, scoped commits, reviewable PR descriptions, linked real Issues, and include `git status`, tests, evidence paths in PRs. Never directly push unreviewed policy changes to protected `main`. Never force-push or rebase others' work without consent.
- Only I can legitimately author my changes. Shaheer and Momin must author their own genuine commits/reviews on their accounts. Prepare instructions for them, but don't fake their participation. Track owners as proposed until confirmed.
- If a defect causes a failure, preserve failing evidence, create the issue only when reproduced, fix it with new tests and a separate PR when approved, and don't auto-close unrelated Issues.
- After approved merge, update local `main` safely, retaining all files locally. Verify push, PR links, status checks and document visibility in Explorer.

## 10. Communication and stage completion contract

Don't ask me to re-upload things already in the accessible workspace. Ask one precise question only when truly blocked by unavailable files, credentials, account permissions, teammate review, a business-policy choice or unsafe/destructive action.

For EACH completed stage give me:
1. What was found vs what changed (exact paths and commits).
2. Commands run, real pass/fail counts, measured metrics, and evidence files.
3. Whether dev database remained untouched.
4. Local file paths that I can open in File Explorer and corresponding GitHub PR/issue links when applicable.
5. What I must personally do now (only if necessary) and how to do it step-by-step.
6. Updated Word report path and what was added.
7. Next stage, remaining blockers, and a copyable precise resume instruction if execution stopped.

Do not claim that Phase 2 or the overall project is 100% complete unless every mandatory rubric item has real evidence. Continue stages while able, but respect tool/session/approval limitations and don't promise future unsupervised work.

**START NOW with the READ-ONLY AUDIT in Section 2; then fulfill the Phase 1 runtime-validation gate in Section 2A on an ISOLATED test environment before claiming any FR or boundary is runtime verified. Inspect the current local branch and actual GitHub PR #4/Issues #5–#10, reconcile Stage D without making up results, and proceed through the safest remaining stages. Keep a precise test log and the SAME local Word report.**
