import contextlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

# Must be set BEFORE importing app, so the in-memory test database is used.
TEST_DB_URI = "sqlite://"
os.environ["MEDIHUB_DATABASE_URI"] = TEST_DB_URI

import pytest
from app import app
from database import db
from seed_db import (
    create_admin_user,
    create_sample_doctors,
    create_sample_availability,
    create_sample_patients,
)


@pytest.fixture()
def client():
    app.config.update(TESTING=True, MAIL_SUPPRESS_SEND=True, PROPAGATE_EXCEPTIONS=False)
        # Flask-Mail reads MAIL_SUPPRESS_SEND only once, when Mail(app) is created
    # at import time, so changing the config above is too late. Switch the
    # already-created mail extension to suppress mode so no SMTP connection
    # is ever opened during tests.
    app.extensions["mail"].suppress = True
    with app.app_context():
        # Safety: refuse to run unless this is the in-memory test database.
        assert str(db.engine.url) == TEST_DB_URI, (
            "Refusing to run: engine points to %s" % db.engine.url
        )
        db.drop_all()
        db.create_all()
        # seed_db.py prints a check-mark character; on Windows consoles using
        # cp1252 that raises UnicodeEncodeError when pytest runs with -s.
        # Silence the seed output (the app code is not modified).
        with contextlib.redirect_stdout(io.StringIO()):
            create_admin_user()
            create_sample_doctors()
            create_sample_availability()
            create_sample_patients()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
