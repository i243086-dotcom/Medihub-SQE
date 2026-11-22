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
    app.config.update(TESTING=True, MAIL_SUPPRESS_SEND=True)
    with app.app_context():
        # Safety: refuse to run unless this is the in-memory test database.
        assert str(db.engine.url) == TEST_DB_URI, (
            "Refusing to run: engine points to %s" % db.engine.url
        )
        db.drop_all()
        db.create_all()
        create_admin_user()
        create_sample_doctors()
        create_sample_availability()
        create_sample_patients()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
