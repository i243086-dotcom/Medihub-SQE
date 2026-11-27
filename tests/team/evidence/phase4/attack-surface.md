# MediHub defensive attack-surface inventory

Production source is the integrated Phase 3 tree at `436c9ff1b6d9fd29c717be719ec187ce0b93f37d`. This inventory covers selected booking and cancellation operations plus the adjacent status and schedule operations that affect them.

| Method and route | Inputs and affected data | Access and defensive control | Risk |
|---|---|---|---|
| GET `/` and `/static/*` | Path and app assets | Public Flask-served Vue shell. API authentication is separate. | Injected or untrusted frontend scripts could read browser storage. |
| POST `/api/auth/login` | Username and password. Reads User and returns a bearer token. | Public entry, password hash and active account checked. | Credential theft or token disclosure. |
| GET `/api/auth/me` | JWT identity. Reads User and role profile. | Valid bearer token. Profile resolved from identity. | Unauthorized profile disclosure. |
| POST `/api/auth/logout` | Client session and storage. | Vue removes the token. Server logout is informational. | A previously disclosed token can remain valid until expiry. |
| GET `/api/patient/dashboard`, `/departments`, `/doctors` (under `/api/patient`) | Active specialties, doctors, patient dashboard counts and appointment metadata. Optional `department` on doctor listing. | Patient role for dashboard and doctor listing. Patient or admin for departments. | Unintended metadata disclosure. |
| GET `/api/patient/available-slots` | `doctor_id`, `date`. Reads Doctor, DoctorAvailability and occupied Appointment slots. | Patient or admin JWT. Input checks plus doctor availability and appointment status. | Enumeration or inconsistent availability. |
| GET `/api/patient/doctor/availability/<doctor_id>` | Numeric doctor ID. Reads Doctor and DoctorAvailability. | Patient role, active doctor check. | Out-of-scope provider schedule data. |
| GET `/api/patient/appointments` | Derives patient from token identity. Reads that patient's appointments. | Patient bearer token and identity-scoped query. | Another patient's booking details disclosed. |
| POST `/api/patient/appointments` | `doctor_id`, `appointment_date`, `appointment_time`, optional `notes`. Reads Patient, Doctor, DoctorAvailability and Appointment, then inserts Appointment. | Patient JWT, eligibility, valid doctor/date/slot and conflict checks backed by SQLite constraints. | Unauthorized booking, duplicate reservation or unwanted text disclosure. |
| DELETE `/api/patient/appointments/<appointment_id>` | Numeric appointment ID. Changes booked Appointment to cancelled, updates its timestamp and attempts patient and doctor notifications. | Patient JWT, patient-owner predicate and status validation. | Cross-patient cancellation or invalid state change. |
| GET `/api/doctor/dashboard`, `/api/doctor/appointments` | JWT doctor identity, optional `date`, `status`, `time_filter` for list. Reads assigned appointments and linked records. | Doctor JWT and `doctor_id` query scope. | Access to another doctor's appointments or attached patient data. |
| PUT `/api/doctor/appointments/<appointment_id>/status` | Appointment ID and requested status. Updates an assigned appointment. | Separate doctor route, ownership and status validation. | Appointment lifecycle misuse. Prior reopening policy remains outside Phase 4. |
| GET `/api/doctor/availability`, `/api/doctor/available-slots`, POST `/api/doctor/set-slots` | Doctor identity, date or date range, morning/evening availability. Reads or writes DoctorAvailability. | Doctor JWT and own profile. | A clinician's changes affect future capacity. |

User holds identity, password hash, active state and role. Patient and Doctor link back to User. DoctorAvailability records date and period for a Doctor. Appointment binds Patient and Doctor with date, start time and status. The browser never supplies the authenticated patient identity in the booking payload.

Source references are [Flask configuration](../../../../backend/app.py), [role decorators](../../../../backend/decorators.py), [auth routes](../../../../backend/routes/auth.py), [patient routes](../../../../backend/routes/patient.py), [doctor routes](../../../../backend/routes/doctor.py), [models](../../../../backend/models/) and [Vue API transport](../../../../frontend/js/api.js).
