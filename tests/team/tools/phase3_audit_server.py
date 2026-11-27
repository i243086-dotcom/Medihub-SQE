"""Serve the real Flask/Vue application over loopback with synthetic SQLite data."""

import os
from pathlib import Path
from secrets import token_hex
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from werkzeug.serving import make_server


def main():
    root = Path(__file__).resolve().parents[3]
    with TemporaryDirectory(prefix='medihub-phase3-audit-') as folder:
        target = (Path(folder) / 'audit.sqlite').resolve()
        os.environ.update(MEDIHUB_DATABASE_URI=f'sqlite:///{target.as_posix()}', MEDIHUB_JWT_SECRET_KEY=token_hex(32))
        sys.path[:0] = [str(root / 'backend'), str(root / 'tests/team')]
        from app import app, db
        from phase2_support import BookingClock, appointment, seed
        from routes import patient

        patient.datetime = BookingClock
        app.extensions['mail'].suppress = True
        with app.app_context():
            assert Path(db.engine.url.database).resolve() == target
            db.create_all()
            seed()
            appointment()
            db.session.commit()
        with make_server('127.0.0.1', 5001, app) as server:
            print('Audit app ready at http://127.0.0.1:5001', flush=True)
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                subprocess.run(sys.argv[1:], check=True)
            finally:
                server.shutdown()
                worker.join()
                with app.app_context():
                    db.engine.dispose()


if __name__ == '__main__':
    main()
