# Coverage scope: server-side business logic for booking and cancellation

The 100% statement and branch target applies only to the functions below.
Line ranges are from the baseline source, from the first decorator to the function's last line (measured with tests/team/tools/function_ranges.py). Re-check after the Stage F extraction.

| File | Function | Lines | Rules |
|---|---|---|---|
| backend/routes/patient.py | get_available_slots | 80-161 | BR-01 |
| backend/routes/patient.py | get_appointments | 184-205 | BR-04 |
| backend/routes/patient.py | book_appointment | 208-318 | BR-01, BR-02 |
| backend/routes/patient.py | cancel_appointment | 321-388 | BR-03, BR-04 |
| backend/routes/doctor.py | update_appointment_status | 171-228 | BR-03 (doctor state changes) |
| backend/routes/admin.py | update_appointment | 182-228 | BR-03 (admin state changes) |
| backend/routes/admin.py | toggle_patient_blacklist | 290-307 | BR-02 condition A |
| backend/decorators.py | admin_required, doctor_required, patient_required, patient_or_admin_required | whole file | BR-04 |
| backend/celery_tasks/email_template.py | get_email_template | whole file | called by cancel and doctor status update |
| backend/business_rules/appointment_rules.py | extracted rule functions | whole file | after Stage F |

## Not in scope, with reason
- patient.py dashboard, departments, doctors, history, export, profile and doctor-availability routes: read-only or profile features, not booking or cancellation rules.
- doctor.py dashboard, patient-history, availability, set-slots and profile routes: doctor-side features outside the four rules.
- admin.py doctor and patient management, search and history routes: administration features outside the four rules.
- backend/seed_db.py: sample-data script, not deployed business logic.
- backend/celery_tasks/email.py, imports.py, reminders.py, reports.py: background jobs not invoked by booking or cancellation. email_template.py stays in scope because cancel_appointment and the doctor status update call it.
- backend/models/*: data definitions; the unique constraint is exercised by API tests.

## Known branches to cover or justify in Stage G
- Cancellation email block in cancel_appointment (patient email present or absent, doctor email present or absent, and the except branch that ignores mail failures).
- The same email block in the doctor status update.

## Approval
Approved by team: pending
