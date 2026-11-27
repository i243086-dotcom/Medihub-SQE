# Predeclared Phase 5 acceptance limits

Use the actual booking widget's bearer-authenticated `GET /api/patient/available-slots?doctor_id=1&date=2030-01-16`. Vue calls the endpoint before a patient selects a time. The read-only request exercises Flask, role authentication, SQLite schedule and appointment reads, and slot formatting without consuming appointment capacity. [Patient route](../../../../backend/routes/patient.py) · [Vue API](../../../../frontend/js/api.js)

| Workload | Steady interval | Maximum p95 | Unexpected failure limit |
|---|---:|---:|---:|
| 1 VU, repeated independently | 65 s | ≤250 ms | <1% |
| 5 concurrent VUs, repeated independently | 65 s | ≤500 ms | <1% |

On loopback this small availability read should update the picker within a quarter second under a single user's load. The five-user limit allows scheduling and SQLite/WSGI contention while keeping the picker responsive. The failure rate must stay below one in 100 at either load. These are local engineering criteria for this build and fixture.

Each scored request must return HTTP 200, success true, the requested doctor and date, and the eight fixture-defined hourly slots with the correct times, periods, availability and display labels. Non-200 responses, transport errors and malformed or incorrect successful responses each count once toward the combined unexpected rate. HTTP failures and failed checks are also reported individually.

Authentication and reset are outside the measured window. Each execution retains its target VU count through a 10-second warm-up, a 65-second scored window and a 5-second tail. Starts inside the scored window are tagged steady and their completions count toward throughput over 65 seconds. Fixed 0.25-second per-VU think time models repeated user actions. Native k6 thresholds consume [the versioned configuration](targets.json).
