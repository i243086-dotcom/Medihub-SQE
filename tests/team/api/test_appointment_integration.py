"""Cross-workflow and coordinated booking requests on disposable SQLite."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from threading import Barrier, Thread
from uuid import uuid4

import pytest
import requests
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import event
from werkzeug.serving import make_server

from app import internal_error
from database import db
from phase2_support import TODAY, appointment, booking_payload, seed, snapshots
from routes import doctor
from routes.patient import patient_bp


@pytest.mark.parametrize(("role", "endpoint"), [
    ("ajay", "/api/doctor/appointments/1/status"),
    ("admin", "/api/admin/appointments/1"),
])
@pytest.mark.parametrize("source", ["booked", "cancelled", "canceled", "completed", "available"])
def test_unknown_status_is_rejected(phase2, role, endpoint, source, record_property):
    client, headers = phase2
    appointment(status=source)
    db.session.commit()
    before = snapshots()
    response = client.put(endpoint, json={"status": "unknown-status"}, headers=headers[role])
    after = snapshots()
    record_property("actual_status", response.status_code)
    record_property("db", f"{before} -> {after}")
    assert (response.status_code, after) == (400, before)


STAFF_TRANSITIONS = [
    ("ajay", "/api/doctor/appointments/1/status", ("booked", "cancelled", "completed")),
    ("admin", "/api/admin/appointments/1", ("booked", "cancelled", "canceled", "completed", "available")),
]


@pytest.mark.parametrize(("actor", "endpoint", "destination"), [
    (actor, endpoint, destination)
    for actor, endpoint, destinations in STAFF_TRANSITIONS
    for destination in destinations
])
@pytest.mark.parametrize("source", ["booked", "cancelled", "canceled", "completed", "available"])
def test_recognized_staff_transitions(phase2, actor, endpoint, source, destination, record_property):
    client, headers = phase2
    appointment(status=source)
    db.session.commit()
    before = snapshots()
    result = client.put(endpoint, json={"status": destination}, headers=headers[actor])
    after = snapshots()
    record_property("transition", f"{actor}: {source} -> {destination}")
    record_property("result", f"{result.status_code}: {before} -> {after}")
    assert result.status_code == 200
    assert result.json["data"]["appointment"]["status"] == destination
    assert after == [(*before[0][:5], destination, before[0][6])]


@pytest.mark.parametrize(("params", "expected_offsets"), [
    ({"time_filter": "today"}, [0]),
    ({"time_filter": "upcoming"}, [0, 1]),
    ({"time_filter": "completed"}, [-1, 2]),
    ({}, [-30, -29, -1, 0, 1, 2]),
    ({"time_filter": "unknown", "status": "booked"}, [-30, -29, 0, 1]),
    ({"time_filter": "upcoming", "status": "completed"}, []),
    ({"date": (TODAY - timedelta(days=1)).isoformat()}, [-1]),
    ({"date": TODAY.isoformat()}, [0]),
    ({"date": (TODAY + timedelta(days=1)).isoformat()}, [1]),
])
def test_doctor_date_and_filter_readback(phase2, monkeypatch, params, expected_offsets, record_property):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return TODAY

    monkeypatch.setattr(doctor, "date", FrozenDate)
    client, headers = phase2
    ids = {
        offset: appointment(day=TODAY + timedelta(days=offset), status=status).id
        for offset, status in ((-31, "booked"), (-30, "booked"), (-29, "booked"),
                               (-1, "completed"), (0, "booked"), (1, "booked"), (2, "completed"))
    }
    appointment(day=TODAY, doctor=2, patient=2)
    db.session.commit()
    before = snapshots()
    result = client.get("/api/doctor/appointments", query_string=params, headers=headers["ajay"])
    assert result.status_code == 200
    actual = [row["id"] for row in result.json["data"]["appointments"]]
    record_property("filter_readback", f"{params}: {actual}")
    assert actual == [ids[offset] for offset in expected_offsets]
    assert snapshots() == before


def test_doctor_status_other_owner(phase2):
    client, headers = phase2
    appointment()
    db.session.commit()
    before = snapshots()
    result = client.put("/api/doctor/appointments/1/status", json={"status": "cancelled"},
                        headers=headers["rajesh"])
    assert result.status_code == 404
    assert snapshots() == before


def test_admin_reschedule_conflict_preserves_status_and_notes(phase2):
    from datetime import time
    from phase2_support import TOMORROW

    client, headers = phase2
    appointment()
    appointment(patient=2, hour=time(11))
    db.session.commit()
    before = snapshots()
    result = client.put("/api/admin/appointments/1", json={"appointment_date": TOMORROW.isoformat(),
                        "appointment_time": "11:00", "notes": "should not commit"},
                        headers=headers["admin"])
    # Match Flask's request teardown before checking persisted data.
    db.session.rollback()
    assert result.status_code == 400
    assert snapshots() == before


@pytest.mark.parametrize("collision", ["same-doctor", "same-patient"])
@pytest.mark.parametrize("attempt", range(1, 6))
def test_concurrent_booking_integrity(phase2, tmp_path, collision, attempt, record_property):
    path = (tmp_path / "concurrent.sqlite").resolve()
    if path.exists() or path.parent != tmp_path.resolve():
        raise RuntimeError("Expected a fresh pytest SQLite file")
    server_app = Flask("phase2-concurrent-booking")
    server_app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///" + path.as_posix(),
                             JWT_SECRET_KEY=uuid4().hex, PROPAGATE_EXCEPTIONS=False)
    db.init_app(server_app)
    JWTManager(server_app)
    server_app.register_blueprint(patient_bp, url_prefix="/api/patient")
    server_app.register_error_handler(500, internal_error)
    rendezvous = Barrier(2, timeout=10)

    def synchronize(conn, cursor, statement, parameters, context, executemany):
        # Both normal requests have passed the conflict lookup before either inserts.
        if "WHERE appointments.patient_id =" in statement and statement.lstrip().startswith("SELECT"):
            rendezvous.wait()

    with server_app.app_context():
        if Path(db.engine.url.database).resolve() != path:
            raise RuntimeError("Engine does not point to the temporary SQLite file")
        db.create_all()
        seed()
        event.listen(db.engine, "after_cursor_execute", synchronize)
        actors = ("4", "5" if collision == "same-doctor" else "4")
        tokens = [create_access_token(actor, additional_claims={"role": "patient"}) for actor in actors]
    http = make_server("127.0.0.1", 0, server_app, threaded=True)
    assert http.server_port != 5000
    thread = Thread(target=http.serve_forever, daemon=True)
    thread.start()

    def send(job):
        token, doctor = job
        with requests.Session() as client:
            client.trust_env = False
            result = client.post(f"http://127.0.0.1:{http.server_port}/api/patient/appointments",
                                 headers={"Authorization": "Bearer " + token},
                                 json=booking_payload(doctor=doctor), timeout=18)
            return result.status_code, result.json()["message"]

    try:
        doctors = (1, 1 if collision == "same-doctor" else 2)
        with ThreadPoolExecutor(max_workers=2) as workers:
            responses = sorted(workers.map(send, zip(tokens, doctors)))
        with server_app.app_context():
            persisted = snapshots()
            db.engine.dispose()
    finally:
        http.shutdown()
        thread.join()
        http.server_close()
    record_property("attempt", attempt)
    record_property("http_responses", str(responses))
    record_property("db_rows", str(persisted))
    assert len(persisted) == 1, persisted
    assert responses == [(200, "Appointment booked successfully"),
                         (400, "That appointment time conflicts with an existing booking")]
