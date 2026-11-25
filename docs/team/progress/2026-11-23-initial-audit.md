# MediHub initial audit, 23 November 2026 (PKT)

The initial reconciliation was read-only. It covered the seven-page assignment, the tagged and current source, both Word inputs, the Phase 2 guide, the Stage A–D history and the local and GitHub evidence.

## Repository and stages A–D

| Stage | Verified | Pending |
|---|---|---|
| A | `D:/SQE_Project/Medihub` was on `phase2-smoke` at `256efcb`, matching origin. Origin `main` and local `main` matched at `adf2871`. Annotated tag object `7a1b7c8` resolves to `e58ce85` locally and on origin. `53e8dd9` retains seven Phase 1 evidence files. PR #1 merged. GitHub lists three collaborators. | Confirm individual ownership and each student's authored work. The inspected log records Syed's work commits and two merge commits under Shaheer's account. Registration is reported in Word. The sheet was unavailable for verification. |
| B | PR #2 merged. Requirements, branch coverage configuration, coverage scope and captured tooling versions exist. Windows project venv has Flask, pytest, Playwright, PyYAML and installed Chromium. | Team approval of scope and measured coverage. Align scope with availability, role checks, lists, status writers and database constraints. |
| C | PR #3 merged. `app.py` reads `MEDIHUB_DATABASE_URI` before extension initialization and retains the baseline default. Fixture asserts in-memory engine before destructive operations. Two historical pytest logs record 2 passes each. The current dev database hash matched their recorded before/after values. | Re-execute with fresh hash and SMTP checks. |
| D | PR #4 was open, mergeable, blocked pending one approval, with zero submitted reviews, requested reviewers or check runs. Its existing comment links Issues #5–#10. Both archived smoke logs end with 6 failed and 3 passed. The full historical 6 failed and 6 passed is reported in the supplied history. | Archive a fresh full run, reconcile registry and Word traceability, correct the PR description's six-defect wording and get a teammate review and disposition decision. |

The only production source difference between baseline and HEAD was the test database override. The original `upstream` still points to Alok Tripathi's repository. GitHub CLI authenticated as `i243086-dotcom` with ADMIN access to the public team repository. `main` requires one approving review, has no required check, and does not enforce protection for admins. GitHub returned zero workflows and no rulesets. The untracked prompt directory preceded this audit, and the reference directory is locally excluded. The continuous-report input is the only content base available. The Phase 1 DOCX is the layout reference.

The existing development service did not respond at `127.0.0.1:5000`. The SQLite file was inspected in read-only immutable mode. It contained 0 appointments, 5 users, 2 doctors, 2 patients and 28 availability rows. SHA-256 was `27BE0512BD93CFADB49D7819CFF68FE6088334B50B1D2F5A9489D488DF6554F5`. The schema has a unique doctor/date/time across all statuses and unique doctor/date/slot type availability. The dev file was not seeded or reset. The separate runtime audit will verify checkout paths and database engine targets before seeding.

## Phase 1 source reconciliation

| ID | Test basis and implementation in both revisions | Initial classification |
|---|---|---|
| FR-01 | `patient.py:34` groups active doctors by specialization. `patient.py:164` lists active doctors with an optional exact specialization filter. Departments allow patient/admin and doctor listing is patient-only. | Verified in source |
| FR-02 | `patient.py:80–161` emits HH:00 starts at 09–12 and 15–18, labels exact times `available` or `booked`, and removes starts at or before the current IST hour only when the requested date equals today. The route does not check active doctor status. Doctor availability details do at `patient.py:435`. | Verified in source. Past-date behavior needs controlled availability. |
| FR-03 | `patient.py:208–318` inserts and commits a booked row for an eligible request. Rebooking a cancelled slot is separately specified by assumption A-01. The all-status unique constraint conflicts with that assumption. | Verified in source. Rebooking contradicted in Stage D evidence. |
| FR-04 | Route expects `doctor_id`, `appointment_date`, `appointment_time`, optional `notes`. It rejects falsey required fields, missing/inactive doctor, malformed date strings and past dates. Time parser runs outside an error handler and only the date parser's ValueError is caught. | Partial. Malformed time and JSON body contradict A-03 in archived Stage D outputs. |
| FR-05 | Separate booked-only exact date/time queries enforce doctor-slot then patient-time conflict. Only the doctor slot has a database uniqueness rule. | Verified in source. Sequential duplicate POST corroborated by Stage D. Concurrent requests remain untested. |
| FR-06 | `patient.py:321–388` updates the owned booked row and timestamp, commits, then attempts email. It has no cancellation deadline condition. | Verified in source and prior Phase 1 evidence. |
| FR-07 | Owner scoping precedes status checking. Missing/wrong owner return 404. Non-booked returns 400. | Verified in source. Wrong owner corroborated by Stage D. |
| FR-08 | `patient.py:184–205` lists the owning patient's appointments. `doctor.py:104–148` lists the owning doctor's rows with recognized statuses. The default history floor is host date minus 30 days and the upcoming filter includes only booked rows. | Verified in source. Prior evidence shows patient/SQLite readback. Doctor runtime and view filters await verification. |
| FR-09 | `decorators.py:36–44` requires a JWT with the patient claim on both writes. The role comparison returns 403 for authenticated doctor and admin. | Verified in source. |
| FR-10 | `patient.py:214–218` checks the patient's blacklist flag before parsing input. `admin.py:290–307` toggles that flag. | Verified in source. |
| Proposed FR-11 | `doctor.py:171–228` requires the assigned doctor and accepts only `completed`, `cancelled`, `booked` as destinations. Existing state is not consulted. | Observed behavior. Transition policy pending. |
| Proposed FR-12 | `admin.py:182–228` requires admin and accepts status or notes, or reschedules when both date and time are present. No status allowlist is enforced. | Observed behavior. Invalid status handling conflicts with proposed validation. |

BR-01 uses appointment hour bands and today’s hour cutoff. The UI offers exact hourly starts and computes its date minimum from UTC via `toISOString`; the API uses IST for today. The seed uses host local date and creates days 0 through 6. The seed horizon is a data edge. A seven-day booking cap is unsupported by the source. BR-02’s six conceptual eligibility conditions are evaluated as sequential guards with additional profile, JSON and time validations. BR-03 covers the patient cancellation action. BR-04 covers role and row ownership, with separate read permissions for slot and department discovery.

The Vue app switches views under the same page using `currentView` in `frontend/js/app.js`. The booking flow selects Specialty, Doctor, Date and Time, and uses `Confirm Booking`. The appointment list exposes a cancel action for booked rows and a Bootstrap confirmation modal. Verify labels and control states against the rendered UI before using them as test oracles. The upstream OpenAPI spec is a starting point. It omits the `/api` prefix on the patient doctor availability detail, under-specifies validation responses, and needs explicit role and transition contracts.

## Hypotheses and issue reconciliation

| Hypothesis | Initial evidence and disposition |
|---|---|
| H-01 | Archived D1 returns 500 on rebooking and retains the cancelled row, consistent with the database unique constraint. Issue #5 is open and confirmed. |
| H-02 | D4a shows doctor reopening and persists booked. Issue #6 is open and triaged pending team policy. D4b stores arbitrary admin status. Issue #7 is open and confirmed. |
| H-03 | D5a's empty JSON object returns 400. Malformed string time, numeric time and JSON null return 500 with no row. Issues #8–#10 are open and confirmed. #8 and #9 share the missing type/parse validation family. #10 starts earlier at JSON object validation. |
| H-04 | Source applies its time cutoff only to today's lookup. A past date can return slots if historical availability exists. A seeded dataset with no historical availability cannot distinguish that behavior. |
| H-05 | Configured Flask/JWT defaults and debug mode are visible in `backend/app.py` at both revisions. The approved passive runtime security assessment is pending. |
| H-06 | No H-06 definition was located in either supplied Word document, the guide or the history log. BR-01's minute discrepancy has its own documented test basis. A sixth historical hypothesis needs a source before assigning its ID. |

## Execution gates

1. Run the isolated Phase 1 HTTP and Chromium matrix against baseline and current HEAD, then reconcile Stage D and update the one cumulative Word report with verified evidence and an AI-use entry for team review.
2. Obtain genuine reviewer input and the team's decision for PR #4. Keep the six historic pytest failures visible and distinguish the policy case. No workflow currently blocks it on a failing test.
3. Proceed to Stage E once Stage D disposition has been agreed. Docker CLI was found and its engine pipe was unavailable. Port 9000 had no reachable SonarQube. Analysis and its CFG comparison are due.
4. Remaining Section 2 deliverables are the broad white-box suite, decision tables, MCC/MC/DC, generated API tests and two spec changes, six use cases and all flows, mutation including two custom operators and survivor analysis, enforced CI, and the risk and defect management evidence. Pilot test evidence does not satisfy those full deliverables.
5. Assignment Sections 3–7 still require accessibility, passive security, performance/recovery, the package with Git history, genuine ownership and viva readiness, and checked AI disclosure.
