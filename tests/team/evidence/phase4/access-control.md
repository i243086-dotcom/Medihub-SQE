# Executed access-control decisions

All seven access decisions and the separate header test passed in Chromium. Each rejected action reached Flask and its SQLite readback matched the before-state. The application displayed success on the two patient UI workflows. Denial messages came from the actual browser HTTP responses, with no added app UI.

| ID and account | Decision and route | Expected | Observed in Chromium | SQLite before → after |
|---|---|---|---|---|
| [P4-01](P4-01.json) patient Arjun | POST `/api/patient/appointments` | Allow, HTTP 200 | Booking confirmation and 200 | 0 rows → 1 owned booked row |
| [P4-02](P4-02.json) doctor Ajay | POST `/api/patient/appointments` | Deny, HTTP 403 | 403, Patient access only | 0 → 0 rows |
| [P4-03](P4-03.json) patient Arjun | DELETE `/api/patient/appointments/1` | Allow own booking, HTTP 200 | Cancellation confirmation and Cancelled row | 1 booked → same row cancelled |
| [P4-04](P4-04.json) doctor Ajay | DELETE `/api/patient/appointments/1` | Deny, HTTP 403 | 403, Patient access only | 1 booked → unchanged |
| [P4-05](P4-05.json) patient Vikram | DELETE `/api/patient/appointments/1` | Deny nonowner, HTTP 404 | 404, Appointment not found | 1 booked → unchanged |
| [P4-06](P4-06.json) anonymous | POST `/api/patient/appointments` | Deny, HTTP 401 | 401, Missing Authorization Header | 0 → 0 rows |
| [P4-07](P4-07.json) doctor Ajay | GET `/api/doctor/appointments` | Allow assigned read, HTTP 200 | Only assigned row returned and Cancelled shown | 2 rows → unchanged |

## Corroborated controls

**P4-C01 | Authentication, role and ownership.** ZAP observed the bearer header on authenticated appointment requests. Flask's `JWT_TOKEN_LOCATION` is headers. Role decorators validate the JWT and its role claim. Cancellation filters by both appointment ID and authenticated patient, then checks its state. Doctor readback filters on the authenticated doctor's ID. The denied anonymous request carried no bearer. [Playwright HTML](playwright.html) · [ZAP message evidence](zap-observed-requests.json) · [Flask configuration](../../../../backend/app.py) · [Role checks](../../../../backend/decorators.py)

**P4-C02 | Browser transport and origin controls.** Successful login returned a token body with no Set-Cookie. Chromium had zero cookies and a token was present in localStorage. The application sent bearer headers on protected requests. A local OPTIONS request representing an untrusted origin returned 200 with no Access-Control-Allow-* headers. ZAP message 141 corroborates the preflight. Cookie attributes are inapplicable to the observed authentication mechanism. A token in localStorage is accessible to scripts in the same origin, and these tests use development HTTP. [Transport test](transport.json) · [ZAP headers](zap-observed-requests.json) · [Client transport](../../../../frontend/js/api.js)
