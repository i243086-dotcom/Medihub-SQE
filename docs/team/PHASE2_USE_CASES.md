# Phase 2 formal use cases

The 30 unique native result nodes below are from the historical passing Chromium run. Expectations describe the archived tested flows. The correction does not change application UI behavior. No new screenshots were generated. Primary technical ownership does not replace the agreed UC ownership.

[Executable source](../../tests/team/e2e/test_appointment_flows.py) · [Native Playwright/pytest HTML](../../tests/team/evidence/phase2/independent-closure/final-ci/browser/browser.html) · [Native JUnit](../../tests/team/evidence/phase2/independent-closure/final-ci/browser/browser.xml)

## UC01 Discover a doctor

Owner **Ayaan**. Actor **Patient**. Requirements **FR-01**.

Trigger and preconditions. Open Book Appointment after synthetic sign-in. Active Cardiology and Neurology doctors exist in the ordinary fixture.

| Flow | Action | Expected screen | SQLite postcondition | Actual native node and verdict |
|---|---|---|---|---|
| UC01-N | Choose Cardiology then Ajay. | Date control appears. | No appointment row. | test_uc01_discover_doctor[chromium-UC01-N] · PASS |
| UC01-A1 | Choose Neurology then Rajesh. | Date control appears for alternative doctor. | No appointment row. | test_uc01_discover_doctor[chromium-UC01-A1] · PASS |
| UC01-A2 | Open doctor Profile and choose Book Appointment from it. | Doctor Profile opens, then date control appears. | No appointment row. | test_uc01_discover_doctor[chromium-UC01-A2] · PASS |
| UC01-E1 | Mark the Neurology doctor inactive in the fixture; open booking. | Neurology hidden; Cardiology remains. | No appointment row. | test_uc01_discover_doctor[chromium-UC01-E1] · PASS |
| UC01-E2 | Attempt to proceed before choosing a specialty/doctor. | Confirm disabled and date input absent. | No appointment row. | test_uc01_discover_doctor[chromium-UC01-E2] · PASS |

## UC02 Select appointment date

Owner **Ayaan**. Actor **Patient**. Requirements **FR-02, FR-04**.

Trigger and preconditions. Fill the date control after selecting a doctor. Fixture uses a controlled clock and configured days.

| Flow | Action | Expected screen | SQLite postcondition | Actual native node and verdict |
|---|---|---|---|---|
| UC02-N | Choose tomorrow. | 09:00 and 15:00 enabled. | No appointment row. | test_uc02_schedule_date[chromium-UC02-N] · PASS |
| UC02-A1 | Choose today before cutoff. | 09:00 and 15:00 enabled. | No appointment row. | test_uc02_schedule_date[chromium-UC02-A1] · PASS |
| UC02-A2 | Choose last configured date, day 6. | 09:00 and 15:00 enabled. | No appointment row. | test_uc02_schedule_date[chromium-UC02-A2] · PASS |
| UC02-E1 | Choose day 7 with no configured slots. | No slots; Confirm disabled, without min-date underflow. | No appointment row. | test_uc02_schedule_date[chromium-UC02-E1] · PASS |
| UC02-E2 | Choose yesterday. | Date underflows minimum; no slots and Confirm disabled. | No appointment row. | test_uc02_schedule_date[chromium-UC02-E2] · PASS |

## UC03 Book an appointment

Owner **Shaheer**. Actor **Patient**. Requirements **FR-03, FR-05**.

Trigger and preconditions. Submit an available slot with a valid eligible patient and selected active doctor/day.

| Flow | Action | Expected screen | SQLite postcondition | Actual native node and verdict |
|---|---|---|---|---|
| UC03-N | Choose 09:00, enter visit note and confirm. | Appointment booked successfully! | One exact booked row with note. | test_uc03_submit_booking[chromium-UC03-N] · PASS |
| UC03-A1 | Choose 15:00 and confirm. | Appointment booked successfully! | One booked row at 15:00. | test_uc03_submit_booking[chromium-UC03-A1] · PASS |
| UC03-A2 | Choose 10:00 and leave notes blank. | Appointment booked successfully! | One booked row with blank notes. | test_uc03_submit_booking[chromium-UC03-A2] · PASS |
| UC03-E1 | Open date with another patient already booked at 09:00. | Occupied slot and Confirm disabled. | Existing other-patient row preserved. | test_uc03_submit_booking[chromium-UC03-E1] · PASS |
| UC03-E2 | A second patient books after the first patient selects 09:00. | Submission displays slot is already booked. | Existing snapshot preserved. | test_uc03_submit_booking[chromium-UC03-E2] · PASS |

## UC04 Read the patient appointment list

Owner **Shaheer**. Actor **Patient**. Requirements **FR-07, FR-08**.

Trigger and preconditions. Open My Appointments after signing in with the seeded patient. Rows vary by flow.

| Flow | Action | Expected screen | SQLite postcondition | Actual native node and verdict |
|---|---|---|---|---|
| UC04-N | View an owned booked row. | Ajay row visible as Booked. | Rows unchanged. | test_uc04_patient_appointment_list[chromium-UC04-N] · PASS |
| UC04-A1 | View mixed owned rows. | Ajay Booked and Rajesh Cancelled. | Rows unchanged. | test_uc04_patient_appointment_list[chromium-UC04-A1] · PASS |
| UC04-A2 | Open View Details on cancelled row. | Appointment History Details visible. | Rows unchanged. | test_uc04_patient_appointment_list[chromium-UC04-A2] · PASS |
| UC04-E1 | Open when no appointments exist. | No appointments found. | Rows unchanged. | test_uc04_patient_appointment_list[chromium-UC04-E1] · PASS |
| UC04-E2 | Open when the only row has another owner. | No appointments found; other row absent. | Other patient row unchanged. | test_uc04_patient_appointment_list[chromium-UC04-E2] · PASS |

## UC05 Cancel or keep a booking

Owner **Momin**. Actor **Patient**. Requirements **FR-06, FR-07**.

Trigger and preconditions. Open My Appointments. Start with an owned booked row for normal or alternate flows.

| Flow | Action | Expected screen | SQLite postcondition | Actual native node and verdict |
|---|---|---|---|---|
| UC05-N | Choose Cancel and Yes, Cancel Appointment. | Modal closes; success and Cancelled status shown. | Same ID changes once to cancelled. | test_uc05_cancel_appointment[chromium-UC05-N] · PASS |
| UC05-A1 | Choose No, Keep it. | Modal closes; Booked persists. | Rows unchanged. | test_uc05_cancel_appointment[chromium-UC05-A1] · PASS |
| UC05-A2 | Close dialog without confirming. | Modal closes; Booked persists. | Rows unchanged. | test_uc05_cancel_appointment[chromium-UC05-A2] · PASS |
| UC05-E1 | Inspect an already cancelled row. | Cancelled visible and cancel control absent. | Rows unchanged. | test_uc05_cancel_appointment[chromium-UC05-E1] · PASS |
| UC05-E2 | Inspect a completed row. | Completed visible and cancel control absent. | Rows unchanged. | test_uc05_cancel_appointment[chromium-UC05-E2] · PASS |

## UC06 Read shared appointment as doctor

Owner **Momin**. Actor **Patient then assigned doctor; other doctor for negative case**. Requirements **FR-08, FR-09**.

Trigger and preconditions. Open doctor appointments; a shared appointment is present. Normal path starts with an owned booked row.

| Flow | Action | Expected screen | SQLite postcondition | Actual native node and verdict |
|---|---|---|---|---|
| UC06-N | Patient cancels and signs out; assigned doctor signs in. | Doctor sees Cancelled for the patient. | Readback preserves the already-cancelled row. | test_uc06_doctor_readback[chromium-UC06-N] · PASS |
| UC06-A1 | Assigned doctor opens a booked row. | Booked visible. | Rows unchanged. | test_uc06_doctor_readback[chromium-UC06-A1] · PASS |
| UC06-A2 | Assigned doctor opens a completed row. | Completed visible. | Rows unchanged. | test_uc06_doctor_readback[chromium-UC06-A2] · PASS |
| UC06-E1 | Unassigned doctor opens the list. | No Appointments and patient row absent. | Rows unchanged. | test_uc06_doctor_readback[chromium-UC06-E1] · PASS |
| UC06-E2 | Doctor opens assigned view and checks for patient booking action. | Patient booking tab absent. | Rows unchanged. | test_uc06_doctor_readback[chromium-UC06-E2] · PASS |
