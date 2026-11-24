"""Booking invariants across ORM writes and the offline SQLite migration."""

from contextlib import closing
from sqlite3 import IntegrityError as SQLiteIntegrityError
import sqlite3

import pytest
from sqlalchemy.exc import IntegrityError

from appointment_slots import commit_appointment
from database import db
from migrate_appointment_slots import migrate
from phase2_support import appointment, booking_payload, snapshots


@pytest.mark.parametrize(("actor", "route"), [
    ("arjun", "/api/patient/appointments"),
    ("ajay", "/api/doctor/appointments/1/status"),
    ("admin", "/api/admin/appointments/1"),
])
def test_late_booking_conflict_rolls_back(phase2, monkeypatch, actor, route):
    client, headers = phase2
    appointment(status="cancelled")
    db.session.commit()
    before = snapshots()

    def reject_commit():
        origin = SQLiteIntegrityError(
            "UNIQUE constraint failed: appointments.doctor_id, appointments.appointment_date, appointments.appointment_time"
        )
        origin.sqlite_errorcode = sqlite3.SQLITE_CONSTRAINT_UNIQUE
        raise IntegrityError(None, None, origin)

    monkeypatch.setattr(db.session, "commit", reject_commit)
    if actor == "arjun":
        result = client.post(route, json=booking_payload(), headers=headers[actor])
    else:
        result = client.put(route, json={"status": "booked", "notes": "must roll back"}, headers=headers[actor])
    assert result.status_code == 400
    assert result.get_json()["success"] is False
    assert result.get_json()["message"] == "That appointment time conflicts with an existing booking"
    assert snapshots() == before


@pytest.mark.parametrize("sqlite_code", [sqlite3.SQLITE_CONSTRAINT_FOREIGNKEY, sqlite3.SQLITE_CONSTRAINT_UNIQUE])
def test_unrelated_integrity_failure_is_not_reported_as_slot_conflict(phase2, monkeypatch, sqlite_code):
    origin = SQLiteIntegrityError("Unrelated database constraint")
    origin.sqlite_errorcode = sqlite_code
    failure = IntegrityError(None, None, origin)

    def reject_commit():
        raise failure

    monkeypatch.setattr(db.session, "commit", reject_commit)
    with pytest.raises(IntegrityError) as caught:
        commit_appointment()
    assert caught.value is failure
    assert snapshots() == []


def test_free_slot_reopening_still_respects_new_doctor_constraint(phase2):
    client, headers = phase2
    appointment(status="cancelled")
    appointment(patient=2)
    db.session.commit()
    before = snapshots()
    response = client.put("/api/doctor/appointments/1/status", headers=headers["ajay"],
                          json={"status": "booked", "notes": "must roll back"})
    assert response.status_code == 400
    assert snapshots() == before


LEGACY = """
CREATE TABLE patients (id INTEGER PRIMARY KEY);
CREATE TABLE doctors (id INTEGER PRIMARY KEY);
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20),
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    CONSTRAINT unique_doctor_slot UNIQUE (doctor_id, appointment_date, appointment_time)
);
CREATE TABLE treatments (id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL REFERENCES appointments(id));
CREATE INDEX history_patient ON appointments (patient_id);
INSERT INTO patients VALUES (1), (2);
INSERT INTO doctors VALUES (1), (2);
"""
INSERT = """
INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, appointment_time, status)
VALUES (?, ?, ?, '2030-01-16', '10:00:00.000000', ?)
"""


def test_migration_preserves_cancelled_history_foreign_keys_and_indexes(tmp_path):
    path = tmp_path / "legacy.sqlite"
    with closing(sqlite3.connect(path)) as legacy, legacy:
        legacy.executescript(LEGACY)
        legacy.execute(INSERT, (1, 1, 1, "cancelled"))
        legacy.execute("INSERT INTO treatments VALUES (1, 1)")
    assert migrate(path)
    assert not migrate(path)
    with closing(sqlite3.connect(path)) as upgraded, upgraded:
        upgraded.execute("PRAGMA foreign_keys = ON")
        upgraded.execute(INSERT, (2, 1, 1, "booked"))
        with pytest.raises(SQLiteIntegrityError):
            upgraded.execute(INSERT, (3, 2, 1, "booked"))
        with pytest.raises(SQLiteIntegrityError):
            upgraded.execute(INSERT, (4, 1, 2, "booked"))
        assert upgraded.execute("SELECT id, status FROM appointments ORDER BY id").fetchall() == [
            (1, "cancelled"), (2, "booked"),
        ]
        assert upgraded.execute("SELECT * FROM treatments").fetchall() == [(1, 1)]
        assert upgraded.execute("PRAGMA foreign_key_check").fetchall() == []
        assert "history_patient" in {row[1] for row in upgraded.execute("PRAGMA index_list(appointments)")}


def test_migration_rolls_back_existing_patient_conflicts(tmp_path):
    path = tmp_path / "legacy_conflict.sqlite"
    with closing(sqlite3.connect(path)) as legacy, legacy:
        legacy.executescript(LEGACY)
        legacy.executemany(INSERT, [(1, 1, 1, "booked"), (2, 1, 2, "booked")])
    with pytest.raises(SQLiteIntegrityError):
        migrate(path)
    with closing(sqlite3.connect(path)) as legacy:
        ddl = legacy.execute("SELECT sql FROM sqlite_schema WHERE name = 'appointments'").fetchone()[0]
        assert "CONSTRAINT unique_doctor_slot UNIQUE" in ddl
        assert legacy.execute("SELECT id, status FROM appointments ORDER BY id").fetchall() == [
            (1, "booked"), (2, "booked"),
        ]
        assert legacy.execute("SELECT name FROM sqlite_schema WHERE name = 'appointments_rebuilt'").fetchone() is None
