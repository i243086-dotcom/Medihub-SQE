import contextlib
import io
import os
import sys
from hashlib import sha256
from secrets import token_hex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

# Must be set BEFORE importing app, so the in-memory test database is used.
TEST_DB_URI = "sqlite://"
os.environ["MEDIHUB_DATABASE_URI"] = TEST_DB_URI
STAGE_D_CREDENTIALS = {"admin": "admin", "ajay": "ajay.kumar123", "rajesh": "rajesh",
                       "arjun": "arjun", "vikram": "vikram"}

import pytest
from app import app
from database import db
from seed_db import (
    create_admin_user,
    create_sample_doctors,
    create_sample_availability,
    create_sample_patients,
)
from flask_jwt_extended import create_access_token
from phase2_support import BookingClock, IDENTITIES, seed
from routes import patient


class SyntheticHeaders(dict):
    def __repr__(self):
        return "<synthetic authorization header omitted>"


@pytest.fixture(scope="session", autouse=True)
def protected_dev_database():
    path = ROOT / "backend/instance/medihub-database.db"

    def digest():
        return sha256(path.read_bytes()).hexdigest() if path.is_file() else None

    before = digest()
    print(f"Protected development DB SHA-256 before: {before or 'absent'}")
    yield
    after = digest()
    print(f"Protected development DB SHA-256 after: {after or 'absent'}")
    assert before == after, "Development database changed during the test session"


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
            create_admin_user(STAGE_D_CREDENTIALS)
            create_sample_doctors(STAGE_D_CREDENTIALS)
            create_sample_availability()
            create_sample_patients(STAGE_D_CREDENTIALS)
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def phase2(monkeypatch):
    import smtplib

    smtp_calls = []

    def block_smtp(*args, **kwargs):
        smtp_calls.append(True)
        raise RuntimeError("SMTP forbidden in tests")

    monkeypatch.setattr(smtplib, "SMTP", block_smtp)
    monkeypatch.setattr(smtplib, "SMTP_SSL", block_smtp)
    monkeypatch.setattr(patient, "datetime", BookingClock)
    app.config.update(TESTING=True, MAIL_SUPPRESS_SEND=True, PROPAGATE_EXCEPTIONS=False)
    monkeypatch.setitem(app.config, "JWT_SECRET_KEY", token_hex(32))
    monkeypatch.setattr(app.extensions["mail"], "suppress", True)
    monkeypatch.setattr(app.extensions["mail"], "default_sender", "audit@example.test")
    with app.app_context():
        if str(db.engine.url) != TEST_DB_URI:
            raise RuntimeError("Phase 2 requires a disposable in-memory database")
        db.drop_all()
        db.create_all()
        seed()
        tokens = {
            user: SyntheticHeaders(Authorization="Bearer " + create_access_token(
                str(user_id), additional_claims={"role": role}
            ))
            for user, (user_id, role) in IDENTITIES.items()
        }
        try:
            yield app.test_client(), tokens
        finally:
            db.session.remove()
            db.drop_all()
            assert not smtp_calls
