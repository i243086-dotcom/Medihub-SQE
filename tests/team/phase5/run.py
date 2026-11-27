"""Run the predeclared k6 experiment with a fresh copy of one disposable fixture."""

import argparse
from contextlib import closing
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

from protect_summary import publish_summary


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGETS = HERE.parent / "evidence/phase5/targets.json"
CONFIG = json.loads(TARGETS.read_text(encoding="utf-8"))
PROTECTED = ROOT / "backend/instance/medihub-database.db"
DASHBOARD = "http://127.0.0.1:5665"
TABLES = ("users", "patients", "doctors", "doctor_availability", "appointments", "treatments")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def snapshot(path):
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as connection:
        return {
            "sha256": digest(path),
            "counts": {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                       for table in TABLES},
            "journal_mode": connection.execute("PRAGMA journal_mode").fetchone()[0],
        }


def app_process(mode, path):
    path = path.resolve()
    if (path.suffix != ".sqlite" or not path.parent.name.startswith("medihub-phase5-")
            or path.parent.parent != Path(tempfile.gettempdir()).resolve() or path == PROTECTED.resolve()):
        raise ValueError("Phase 5 requires its own disposable SQLite file in the OS temporary directory")

    os.environ["MEDIHUB_DATABASE_URI"] = f"sqlite:///{path.as_posix()}"
    os.environ["MEDIHUB_SECRET_KEY"] = secrets.token_hex(32)
    os.environ["MEDIHUB_JWT_SECRET_KEY"] = secrets.token_hex(32)
    sys.path[:0] = [str(ROOT / "backend"), str(HERE.parent)]
    from app import app
    from database import db
    from models import Patient, User
    from phase2_support import BookingClock, seed
    from routes import patient
    from werkzeug.security import generate_password_hash

    patient.datetime = BookingClock
    app.extensions["mail"].suppress = True
    with app.app_context():
        assert Path(db.engine.url.database).resolve() == path
        if mode == "seed":
            db.create_all()
            seed()
            password_hash = generate_password_hash(os.environ["MEDIHUB_P5_PASSWORD"])
            for number in range(1, 6):
                user_id = 10 + number
                username = f"phase5-patient-{number}"
                db.session.add(User(id=user_id, username=username, email=username + "@example.test",
                                    password_hash=password_hash, role="patient", is_active=True))
                db.session.add(Patient(id=user_id, user_id=user_id, name=f"Phase 5 Patient {number}"))
            db.session.commit()
            return
        print(json.dumps({
            "engine_path": db.engine.url.database,
            "busy_timeout_ms": db.session.connection().exec_driver_sql("PRAGMA busy_timeout").scalar(),
            "sqlite_version": sqlite3.sqlite_version
        }), flush=True)
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False, threaded=True)


def wait_http(url, process):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError(f"Process exited {process.returncode} before {url} was ready")
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return {"url": url, "status": response.status, "observed_utc": utc()}
        except (URLError, TimeoutError):
            time.sleep(0.15)
    raise RuntimeError(f"No successful HTTP response from {url}")


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def dump(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_one(run, k6, output, template, environment, private):
    output.mkdir()
    server_env = {**environment, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    for port in (5001, 5665):
        with socket.socket() as probe:
            probe.settimeout(0.5)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"A different process is listening on loopback port {port}")
    path = template.with_name(output.name + ".sqlite")
    shutil.copyfile(template, path)
    variables = {
        "MEDIHUB_P5_RUN": run["id"], "K6_NO_USAGE_REPORT": "true",
        "K6_WEB_DASHBOARD": "true", "K6_WEB_DASHBOARD_HOST": "127.0.0.1",
        "K6_WEB_DASHBOARD_PORT": "5665", "K6_WEB_DASHBOARD_PERIOD": "5s",
        "K6_WEB_DASHBOARD_EXPORT": str(output / "dashboard.html")
    }
    native_summary = private / (output.name + "-summary.json")
    command = [k6, "run", "--no-color", "--out", f"json={output / 'metrics.jsonl'}",
               "--summary-export", str(native_summary), str(HERE / "availability.js")]
    data = {
        "run": run, "profile": CONFIG["profiles"][run["profile"]], "targets": CONFIG,
        "targets_commit": git("log", "-1", "--format=%H", "--", str(TARGETS)),
        "targets_sha256": digest(TARGETS), "executed_head": git("rev-parse", "HEAD"),
        "command": command, "environment": variables, "database_path": str(path),
        "k6_version": subprocess.check_output([k6, "version"], text=True).strip(),
        "before": snapshot(path)
    }
    assert data["before"] == snapshot(template)
    dump(output / "run.json", data)
    try:
        with (output / "flask.log").open("wb") as server_log:
            server = subprocess.Popen([sys.executable, __file__, "_serve", str(path)],
                                      env=server_env, cwd=ROOT, stdout=server_log, stderr=subprocess.STDOUT)
            try:
                data["health"] = wait_http(CONFIG["origin"] + "/", server)
                print(f"{run['id']} started with {data['profile']['vus']} VUs at {utc()}", flush=True)
                with (output / "console.log").open("wb") as console:
                    data["k6_started_utc"] = utc()
                    load = subprocess.Popen(command, cwd=ROOT, env={**environment, **variables},
                                            stdout=console, stderr=subprocess.STDOUT)
                    try:
                        data["dashboard_http"] = wait_http(DASHBOARD, load)
                        data["exit_code"] = load.wait(timeout=155)
                    finally:
                        if load.poll() is None:
                            load.kill()
                        data["exit_code"] = load.wait()
                        data["k6_ended_utc"] = utc()
            finally:
                server.terminate()
                server.wait(timeout=10)
    finally:
        if native_summary.exists():
            publish_summary(native_summary, output / "summary.redacted.json")
        data["after"] = snapshot(path)
        dump(output / "run.json", data)
    print(f"{run['id']} exited {data['exit_code']} at {data['k6_ended_utc']}", flush=True)
    assert data["after"] == data["before"], "Read-only load altered the SQLite snapshot"


def main():
    if len(sys.argv) == 3 and sys.argv[1] in {"_seed", "_serve"}:
        app_process(sys.argv[1][1:], Path(sys.argv[2]))
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k6", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run", choices=[run["id"] for run in CONFIG["run_order"]])
    parser.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()
    baseline = CONFIG["application_commit"]
    if git("status", "--porcelain", "--", "backend", "frontend") or git(
            "diff", "--name-only", baseline, "--", "backend", "frontend"):
        raise RuntimeError("The application tree differs from the predeclared build")
    if not git("log", "-1", "--format=%H", "--", str(TARGETS)) or git("status", "--porcelain", "--", str(TARGETS)):
        raise RuntimeError("Commit thresholds before running the experiment")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    protected_before = digest(PROTECTED)
    environment = {**os.environ, "MEDIHUB_P5_PASSWORD": secrets.token_urlsafe(24)}
    private = Path(tempfile.mkdtemp(prefix="medihub-phase5-native-private-"))
    print(f"Unmodified summaries stay in the local private directory {private}", flush=True)
    with tempfile.TemporaryDirectory(prefix="medihub-phase5-") as tmp:
        template = Path(tmp) / "seed.sqlite"
        subprocess.run([sys.executable, __file__, "_seed", str(template)], env=environment, check=True)
        try:
            for run in CONFIG["run_order"]:
                if not args.run or run["id"] == args.run:
                    name = run["id"] if args.attempt == 1 else f"{run['id']}-attempt-{args.attempt}"
                    run_one(run, str(args.k6.resolve()), output / name, template, environment, private)
        finally:
            protected_after = digest(PROTECTED)
            filename = "database-safety.json" if args.attempt == 1 else f"database-safety-{args.attempt}.json"
            dump(output / filename, {"development_before": protected_before,
                                     "development_after": protected_after, "fixture": snapshot(template)})
            assert protected_before == protected_after, "The development database changed"


if __name__ == "__main__":
    main()
