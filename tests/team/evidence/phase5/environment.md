# Phase 5 environment and isolation

The experiments ran on the same Dell Latitude 7410 laptop with Windows 11 Pro build 22000, Intel Core i5-10310U, four physical cores and eight logical processors. The hardware inventory reports 16.83 GB installed RAM and 6.27 GiB available during the series. See [machine.json](machine.json) for the recorded sample. This was a shared laptop environment with the generator and server on the same machine.

- MediHub application build `305918fd27941004bf59766e559937a009ca8eda`, the merge of Phase 4 PR #16. The runner checks that the backend and frontend match this build. The runner and workload revisions are recorded per run.
- Python 3.11.9, Flask 2.3.3, Werkzeug 2.3.7, SQLAlchemy 2.1.9, SQLite 3.45.1 and Grafana k6 OSS 2.4.0 for Windows amd64. The genuine executable and installation evidence are listed in [k6-installation.json](k6-installation.json).
- The real Flask application listens only at `127.0.0.1:5001`, with the standard threaded Werkzeug development server, debug and reloader disabled. The measured route uses patient JWTs obtained through the real login API in k6 setup. Outbound mail is suppressed.
- The runner seeds one reference SQLite file in the current user's temporary directory and copies it byte-for-byte to a new disposable file for each run. The starting dataset is 10 synthetic users, seven patients, two doctors, 28 availability rows, zero appointments and zero treatments. Five synthetic patients authenticate for the workload. The database uses the observed DELETE journal and 5,000 ms busy timeout. Each run records the path, initial and final digest and counts.
- The reused Phase 2 fixture freezes the booking business clock at 2030-01-15 02:30 UTC, equivalent to 08:00 in the application's UTC+05:30 calculation. The query selects the next day. k6 and JWT use wall time. Run records retain UTC timestamps. Human-readable run times use Pakistan Standard Time.
- Recovery uses the established Phase 2 Flask integration fixture, a fresh in-memory SQLite schema and seeded synthetic records. The fixture guards the production database and blocks SMTP.

Development database `backend/instance/medihub-database.db` SHA-256 before and after the series is recorded in [runs/database-safety.json](runs/database-safety.json). The recovery pytest log independently records its before and after hash. No database file, JWT, password or tool executable is included in Git.

The results describe the availability picker with five or fewer paced localhost clients on this laptop. They do not establish production capacity, booking-write throughput, mobile latency or resilience to prolonged outages.
