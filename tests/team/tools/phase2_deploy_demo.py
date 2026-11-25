"""Deploy and probe the checked-out revision in a disposable loopback environment."""

import argparse
from contextlib import closing
from http.client import HTTPConnection
from io import BytesIO
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
from threading import Thread

from werkzeug.serving import make_server


def probe(port, route):
    client = HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        client.request("GET", route)
        response = client.getresponse()
        return response.status, response.read()
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    output = parser.parse_args().output.resolve()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    archive = subprocess.check_output(["git", "archive", revision, "backend", "frontend"])
    original_dir = Path.cwd()
    with TemporaryDirectory(prefix="medihub-loopback-preview-") as folder:
        root = Path(folder).resolve()
        with tarfile.open(fileobj=BytesIO(archive)) as package:
            package.extractall(root, filter="data")
        database = root / "preview.sqlite"
        os.environ["MEDIHUB_DATABASE_URI"] = f"sqlite:///{database.as_posix()}"
        os.environ["MEDIHUB_INITIAL_ADMIN_PASSWORD"] = ""
        backend = root / "backend"
        sys.path.insert(0, str(backend))
        os.chdir(backend)
        try:
            from app import app, db, setup_db

            setup_db()
            with make_server("127.0.0.1", 0, app) as server:
                worker = Thread(target=server.serve_forever)
                worker.start()
                try:
                    home_status, home = probe(server.server_port, "/")
                    auth_status, _ = probe(server.server_port, "/api/auth/me")
                finally:
                    server.shutdown()
                    worker.join()
            with closing(sqlite3.connect(database)) as connection:
                appointments = connection.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
                users = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            with app.app_context():
                db.engine.dispose()
            if (home_status, auth_status, appointments, users) != (200, 401, 0, 0) or b"<title>MediHub" not in home:
                raise RuntimeError("Loopback preview failed its UI, API or disposable database checks")
        finally:
            os.chdir(original_dir)
    result = {"revision": revision, "environment": "phase2-loopback-preview", "bind": "127.0.0.1",
              "frontend_http": home_status, "unauthenticated_api_http": auth_status,
              "appointment_rows": appointments, "user_rows": users, "disposable_data_removed": not root.exists()}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
