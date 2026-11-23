# Phase 2 test design and control plan

## Scope and work tracking

The Section 2 scope is patient appointment discovery, booking, cancellation and related persisted state. Doctor/admin status and availability, applicable guards, notification paths and model constraints are included when they can change or expose appointment state. Independent usability, security, performance and submission phases remain outside this run.

| Work | Planned ownership for team confirmation | Actual milestone |
|---|---|---|
| Static analysis, white box and CI | Syed Ayaan Haider | Phase 2 execution approved on 23 November 2026. Sonar submitted and Actions triggered on that date. |
| API specification, generator and integration | Shaheer Shoaib | Local API/design execution on 23 November 2026. Ownership and review pending. |
| Browser and use cases | Two proposed use cases per person below | Local Chromium execution on 23 November 2026. Ownership sign-off pending. |
| Defect and delivery management | All three members | GitHub triage and evidence review on 23 November 2026. Individual effort and review pending. |

The continuous report records the PERT forecasts of **129.8 person-hours** for Phase 2 and **156.5** including later work. The time log contains 1.5 recorded person-hours for setup. It cannot support a total actual-versus-estimate comparison. The listed ownership and milestone dates are planning assignments or actual test dates. No agreed deadline or additional teammate hours were observed.

Entry requires the baselined test scope, versioned inputs, disposable SQLite and a verified database safety guard. Suspend deployment if a release gate fails, a test writes to the development database, or a critical policy or environment assertion cannot be verified. Independent diagnostics may continue on isolated data. Resume the affected run after validating the corrected fixture, tool or approved policy and repeating the original oracle.

High risks 13–25 receive guard/transition combinations, boundary checks, database readback, mutation and release-gate checks as applicable. Medium risks 6–12 receive EP, real BVA and negative readback. Low risks 1–5 receive the agreed happy path and impact-appropriate regression.

## Decision, transition and boundary design

| Rule | Conditions and expected outcome | Evidence |
|---|---|---|
| BR-01 hour | Morning accepts 09 to 12 and evening 15 to 18. Other hour starts are rejected. For today's date, the start hour must exceed the current IST hour. Future dates do not use that cutoff. Past dates fail booking even with historical availability. | Unit IDs `test_br01_hour_windows`, `test_br01_exact_cutoff`, `test_br01_future_date_has_no_today_cutoff`. The three points for the four limits share 14:00 once. Phase 1 P1-D01 and P1-C-midnight show historical lookup and timezone handling. |
| BR-02 eligibility | A to F are not blacklisted, doctor active, date not past, period available, doctor slot free and patient time free. A false yields 403 first, then B false 404, then first false C/D/E/F 400, then all true 200. Other syntax and slot guards are tested separately. | [All 64 executed combinations](../../tests/team/evidence/phase2/verification/br02-mcc.csv), [six independent pairs](../../tests/team/evidence/phase2/verification/br02-mcdc.csv). The fixture uses independent doctor and patient conflict rows. |
| BR-03 patient state | A role-admitted patient needs an existing owned row and `booked` source state. Booked→cancelled writes once. Wrong owner or no row yields 404. Owned cancelled, completed and available yield 400 and unchanged data. The patient can cancel after the start under A-02. | `test_br03_cancel_transition`, `test_br03_profile_absent`, UC05, Phase 1 P1-A09/P1-A15. |
| BR-04 route and ownership | Unauthorized anonymous writes return 401. Wrong authenticated roles return 403 before data changes. Patient booking/cancellation use only patient permissions. Doctor updates also need the assigned doctor. Admin updates use admin permission and reject unknown state labels. | Generated role cases across twelve operations, `test_br04_patient_writes`, `test_doctor_status_other_owner`, browser UC04/UC06. |
| Doctor/admin transition policy | The test basis defines the permitted actor and recognized status labels. Allowed transitions *between* recognized states from a previously cancelled or completed record still need team confirmation. The historical observed transition matrix and #6 describe behavior. Unknown destinations are rejected from booked, cancelled and completed in the updated build. | Phase 1 P1-doctor-*/P1-admin-* and `test_unknown_status_is_rejected`. |

Ordered date points are yesterday, today, tomorrow, days 5/6/7 on the seeded horizon and a farther explicitly configured availability day. A seeded horizon describes fixture availability. EP cases include required/missing/wrong-type documents and fields, existing/nonexistent resources, active and inactive fixtures, ownership and role. Declared time formatting allows the original minute/range inputs in the current version. The versioned overlay intentionally changes the time pattern and doctor status enum to demonstrate the impact of an unapproved policy. Its failures remain distinct from active acceptance.

The coverage denominator inventories the deployed functions in `phase2_metrics.py`. Profile editing, user registration, non-appointment admin search, report exports and unused background tasks are excluded because they do not decide or read the tested appointment flows. The role helpers, effective status writers, doctor availability, treatment completion, login, model serialization and email template stay in scope. The full measured source/arc list and uncovered locations are reported separately from the stricter unit result.

## Six Chromium use cases

Owners are proposed pending confirmation. Each row maps five unique JUnit IDs to the executable flow. Setup uses seeded synthetic logins, no live email and a disposable SQLite engine on loopback. Every flow checks the visible result and relevant database postcondition.

| Use case and proposed owner | Preconditions and trigger | Normal flow | Alternatives | Exceptions | Postconditions and FR |
|---|---|---|---|---|---|
| UC01 Discover a doctor, Syed | Signed-in patient opens Book Appointment | N Cardiology and Ajay select the date control | A1 Neurology and Rajesh. A2 Doctor Profile then Book Appointment. | E1 An inactive doctor's specialty is absent. E2 Confirm is disabled before selection. | Selection is presented without creating a row, FR-01. |
| UC02 Choose a day, Syed | A doctor is selected and user fills the date control | N Tomorrow shows morning/evening slots. | A1 Today before the cutoff. A2 Last configured seed date. | E1 Beyond configured date shows no slots. E2 Yesterday is below the form minimum. | Visible controls reflect the date and no appointment is written, FR-02/04. |
| UC03 Submit a reservation, Shaheer | Signed-in patient chooses a doctor and configured day | N Morning slot plus notes persists. | A1 Book evening. A2 Book without notes. | E1 Occupied button is disabled. E2 A normal competing reservation before submit triggers the slot-conflict message. | Confirmation and exact persisted row on success. The rejected case preserves the prior row, FR-03/05. |
| UC04 Read patient appointments, Shaheer | Signed-in patient opens My Appointments | N Booked row appears. | A1 Mixed owned states. A2 Cancelled details open. | E1 Empty list. E2 Another patient's row stays absent. | No write and ownership/readback confirmed, FR-07/08. |
| UC05 Cancel or keep, Momin | Owning patient opens a booked row's Cancel action | N Confirm cancel and see Cancelled. | A1 Keep it. A2 Close dialog without saving. | E1 Cancelled row has no Cancel action. E2 Completed row has no Cancel action. | Exactly one status write on confirmation and unchanged rows on other flows, FR-06/07. |
| UC06 Assigned doctor readback, Momin | Patient/doctor accounts and appointment available | N Patient cancels, signs out, and the assigned doctor reads Cancelled. | A1 Assigned doctor reads Booked. A2 Assigned doctor reads Completed. | E1 Unassigned doctor sees an empty list. E2 Doctor has no patient booking tab. | Correct display and unchanged underlying row after readback, FR-08/09. |

The repository [Chromium suite](../../tests/team/e2e/test_appointment_flows.py) asserts these outcomes against the served Vue application. Vue and Bootstrap are fingerprinted. Nonessential third-party browser requests are blocked during tests. The historical Phase 1 flow and the 30 new use-case flows are counted separately.
