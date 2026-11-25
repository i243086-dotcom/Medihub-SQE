"""Compare tagged and current MediHub over loopback using disposable SQLite files."""

import argparse
import io
import json
import os
import platform
import smtplib
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from zipfile import ZipFile

import requests
from werkzeug.serving import make_server

from phase1_cases import api_cases, browser_cases


ROOT = Path(__file__).resolve().parents[3]
DEV_DB = ROOT / "backend/instance/medihub-database.db"
BASELINE = "e58ce855f5fb0c725ece13fa0a44d25486078465"
PKT = timezone(timedelta(hours=5), "PKT")
HOST_DATE = date(2026, 11, 23)
INITIAL_UTC = datetime(2026, 11, 23, 2, 30)
ACCOUNTS = {"arjun": "arjun", "vikram": "vikram", "ajay": "ajay.kumar123",
            "rajesh": "rajesh", "admin": "admin"}


def git(*arguments):
    return subprocess.check_output(["git", "-C", str(ROOT), *arguments])


class HostDate(date):
    @classmethod
    def today(cls):
        return HOST_DATE


class BookingClock(datetime):
    utc = INITIAL_UTC

    @classmethod
    def utcnow(cls):
        return cls.utc


class Audit:
    def __init__(self, db_file, output, revision, port, selected):
        self.db_file = db_file
        self.output = output
        self.output_revision = revision
        self.url = f"http://127.0.0.1:{port}"
        self.selected = selected
        self.case_id = None
        self.results = []
        self.steps = []
        self.client = requests.Session()
        self.client.trust_env = False
        self.tokens = {}

    def db_sql(self, sql, params=()):
        with sqlite3.connect(self.db_file.as_uri() + "?mode=rw", uri=True) as connection:
            return connection.execute(sql, params).fetchall()

    def rows(self):
        return self.db_sql(
            "SELECT id, patient_id, doctor_id, appointment_date, appointment_time, "
            "status, updated_at FROM appointments ORDER BY id"
        )

    def set_clock(self, time):
        BookingClock.utc = datetime.combine(HOST_DATE, datetime.fromisoformat(
            f"{HOST_DATE}T{time}"
        ).time())
        self.steps.append({"clock_utc": BookingClock.utc.isoformat() + "Z"})

    def login(self):
        for name, password in ACCOUNTS.items():
            response = self.client.post(self.url + "/api/auth/login",
                                        json={"username": name, "password": password}, timeout=10)
            response.raise_for_status()
            self.tokens[name] = response.json()["data"]["token"]

    def request(self, method, path, actor="arjun", headers=None, **kwargs):
        headers = dict(headers or {})
        if actor:
            headers["Authorization"] = "Bearer " + self.tokens[actor]
        write = method != "GET"
        before = self.rows() if write else None
        response = self.client.request(method, self.url + path, headers=headers, timeout=10, **kwargs)
        data = response.json() if "application/json" in response.headers.get("Content-Type", "") else {}
        self.steps.append({"method": method, "path": path, "actor": actor, "input":
                           kwargs.get("json", kwargs.get("data")), "query": kwargs.get("params"),
                           "status": response.status_code, "response": sanitize(data),
                           "db_before": before, "db_after": self.rows() if write else None})
        return response.status_code, data

    def case(self, case_id, requirements, expectation, test, *, policy=False):
        if self.selected and case_id not in self.selected:
            return
        self.case_id = case_id
        self.steps = []
        self.db_sql("DELETE FROM appointments")
        self.db_sql("UPDATE doctors SET is_active = 1")
        self.db_sql("UPDATE patients SET is_blacklisted = 0")
        self.db_sql("DELETE FROM doctor_availability WHERE availability_date < ? OR availability_date > ?",
                    (HOST_DATE.isoformat(), (HOST_DATE + timedelta(days=6)).isoformat()))
        self.db_sql("UPDATE doctor_availability SET is_available = 1")
        BookingClock.utc = INITIAL_UTC
        error = None
        try:
            test()
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        result = {"id": case_id, "scope": requirements, "expected": expectation,
                  "verdict": "fail" if error else ("policy pending" if policy else "pass"),
                  "error": error, "steps": self.steps}
        self.results.append(result)
        print(case_id, result["verdict"], error or "", flush=True)


def sanitize(value):
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        private = {"token", "email", "phone", "address", "patient_phone", "medical_history",
                   "emergency_contact"}
        return {key: sanitize(item) for key, item in value.items() if key not in private}
    return value


def run_build(args):
    build = args.build_dir.resolve()
    if ROOT in build.parents or build == ROOT:
        raise RuntimeError("Isolated build must be outside the workspace")
    backend = build / "backend"
    os.chdir(backend)
    sys.path.insert(0, str(backend))
    db_file = (backend / "instance/medihub-database.db").resolve()
    if build not in db_file.parents or db_file == DEV_DB.resolve() or db_file.exists():
        raise RuntimeError("Refusing to seed outside a clean isolated build")
    os.environ["MEDIHUB_DATABASE_URI"] = "sqlite:///" + db_file.as_posix()
    smtp_attempts = []

    def reject_smtp(*a, **k):
        smtp_attempts.append("SMTP constructor called")
        raise RuntimeError("SMTP blocked during audit")

    smtplib.SMTP = smtplib.SMTP_SSL = reject_smtp
    from app import app
    from database import db
    from routes import doctor, patient
    import seed_db

    patient.datetime = BookingClock
    doctor.date = seed_db.date = HostDate
    app.config.update(TESTING=True, DEBUG=False, PROPAGATE_EXCEPTIONS=False,
                      MAIL_SUPPRESS_SEND=True, MAIL_DEFAULT_SENDER="audit@example.test")
    mail = app.extensions["mail"]
    mail.suppress = True
    mail.default_sender = "audit@example.test"
    with app.app_context():
        if Path(db.engine.url.database).resolve() != db_file or db.engine.url.drivername != "sqlite":
            raise RuntimeError("Unexpected database engine. Stopping before schema creation.")
        print("Verified disposable engine:", db.engine.url, flush=True)
        db_file.parent.mkdir(exist_ok=True)
        server = make_server("127.0.0.1", args.port, app)
        try:
            db.create_all()
            seed_db.create_admin_user()
            seed_db.create_sample_doctors()
            seed_db.create_sample_availability()
            seed_db.create_sample_patients()
        except BaseException:
            server.server_close()
            raise

    audit = Audit(db_file, args.output, args.revision, args.port, args.case)
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        if not args.case or args.case != ["P1-UI01"]:
            audit.login()
        api_cases(audit)
        if not args.api_only and (not args.case or "P1-UI01" in args.case):
            try:
                browser_cases(audit, args.assets)
            except Exception as exc:
                audit.results.append({"id": "P1-browser-infrastructure", "scope": "FR-01;FR-02;FR-03;FR-06;FR-08",
                                      "verdict": "untested", "error": str(exc)})
        if args.case and {result["id"] for result in audit.results} != set(args.case):
            raise RuntimeError("One or more requested case IDs did not execute")
    finally:
        server.shutdown()
        server_thread.join()
        server.server_close()
        audit.client.close()
        with app.app_context():
            db.engine.dispose()
    summary = {status: sum(item["verdict"] == status for item in audit.results)
               for status in ("pass", "fail", "policy pending", "untested")}
    report = {"revision": args.revision, "url": audit.url, "database": str(db_file),
              "timestamp_pkt": datetime.now(PKT).isoformat(), "host_seed_date": HOST_DATE.isoformat(),
              "initial_utc": INITIAL_UTC.isoformat() + "Z", "sqlite": sqlite3.sqlite_version,
              "smtp_attempts": smtp_attempts, "summary": summary, "cases": audit.results}
    with (args.output / f"{args.revision}.json").open("x", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2, ensure_ascii=False)
        report_file.write("\n")
    if smtp_attempts:
        raise RuntimeError("SMTP was attempted")
    return int(bool(summary["fail"] or summary["untested"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New directory for raw evidence")
    parser.add_argument("--assets", type=Path, help="Offline Vue and Bootstrap assets")
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--api-only", action="store_true")
    parser.add_argument("--case", action="append")
    parser.add_argument("--build-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--revision", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.port == 5000:
        parser.error("Port 5000 is reserved for the development app")
    args.output = args.output.resolve()
    if args.assets:
        args.assets = args.assets.resolve()
    if args.build_dir:
        return run_build(args)
    tag = git("rev-parse", "baseline-v0^{commit}").decode().strip()
    if tag != BASELINE:
        raise RuntimeError("Original baseline tag points to an unexpected commit")
    branch = git("branch", "--show-current").decode().strip()
    head = git("rev-parse", "HEAD").decode().strip()
    args.output.mkdir(parents=True, exist_ok=False)
    before = sha256(DEV_DB.read_bytes()).hexdigest()
    exit_codes = []
    start = datetime.now(PKT).isoformat()
    try:
        for revision, commit in (("baseline", tag), ("current", head)):
            with TemporaryDirectory(prefix=f"medihub-{revision}-") as folder:
                data = git("archive", "--format=zip", commit, "backend", "frontend")
                with ZipFile(io.BytesIO(data)) as archive:
                    archive.extractall(folder)
                cmd = [sys.executable, "-B", "-X", "utf8", __file__, "--output", str(args.output),
                       "--build-dir", folder, "--revision", revision, "--port", str(args.port)]
                if args.assets:
                    cmd.extend(("--assets", str(args.assets)))
                if args.api_only:
                    cmd.append("--api-only")
                for case in args.case or ():
                    cmd.extend(("--case", case))
                with (args.output / f"{revision}-server.log").open("xb") as log:
                    result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
                print(revision, commit, "exit", result.returncode, flush=True)
                exit_codes.append(result.returncode)
                if sha256(DEV_DB.read_bytes()).hexdigest() != before:
                    raise RuntimeError("Development database changed. Stopping audit.")
    finally:
        fingerprint = {name: sha256((args.assets / name).read_bytes()).hexdigest()
                       for name in ("vue.global.js", "bootstrap.bundle.min.js", "bootstrap.min.css")
                       if args.assets and (args.assets / name).is_file()}
        report = {"branch": branch, "baseline_commit": tag, "current_commit": head,
                  "started_pkt": start, "finished_pkt": datetime.now(PKT).isoformat(),
                  "python": platform.python_version(), "os": platform.platform(),
                  "versions": {name: version(name) for name in ("Flask", "Flask-SQLAlchemy",
                               "Flask-Mail", "playwright", "requests", "SQLAlchemy")},
                  "browser_asset_sha256": fingerprint,
                  "dev_db_before_sha256": before, "dev_db_after_sha256": sha256(DEV_DB.read_bytes()).hexdigest(),
                  "api_only": args.api_only, "exit_codes": exit_codes}
        (args.output / "environment.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return int(any(exit_codes))


if __name__ == "__main__":
    sys.exit(main())
