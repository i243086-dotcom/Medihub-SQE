"""Focused white-box tests of the deployed route decisions and model constraint."""

from datetime import datetime, time, timedelta
from inspect import unwrap

import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from database import db
from mcc import ROWS, case_id, oracle
from models import Doctor, DoctorAvailability, Patient
from phase2_support import (BookingClock, PAST, TODAY, TOMORROW, appointment,
                            availability, booking_payload, snapshots)
from routes import patient


def call_booking(monkeypatch, payload):
    monkeypatch.setattr(patient, "get_current_user_id", lambda: 4)
    with app.test_request_context("/api/patient/appointments", method="POST", json=payload):
        response = app.make_response(unwrap(patient.book_appointment)())
    return response.status_code, response.get_json()


@pytest.mark.parametrize("bits", ROWS, ids=case_id)
def test_br02_all_combinations(phase2, monkeypatch, bits):
    allowed_patient, active_doctor, valid_date, has_availability, free_slot, free_patient = bits
    db.session.get(Patient, 1).is_blacklisted = not allowed_patient
    db.session.get(Doctor, 1).is_active = active_doctor
    day = TOMORROW if valid_date else PAST
    if valid_date:
        row = DoctorAvailability.query.filter_by(doctor_id=1, availability_date=day, slot_type="morning").one()
        row.is_available = has_availability
    else:
        availability(1, day, available=has_availability)
    if not free_slot:
        appointment(doctor=1, patient=2, day=day)
    if not free_patient:
        appointment(doctor=2, patient=1, day=day)
    db.session.commit()
    before = snapshots()

    status, body = call_booking(monkeypatch, booking_payload(day=day))

    expected_status, phrase = oracle(bits)
    assert (status, phrase.lower() in body["message"].lower()) == (expected_status, True), body
    assert body["success"] is (expected_status == 200)
    after = snapshots()
    if expected_status == 200:
        assert before == []
        assert after == [(body["data"]["appointment"]["id"], 1, 1, day.isoformat(), "10:00", "booked", "")]
    else:
        assert after == before


@pytest.mark.parametrize(("hour", "expected"), [
    ("08:00", 400), ("09:00", 200), ("10:00", 200), ("12:00", 200), ("13:00", 400),
    ("14:00", 400), ("15:00", 200), ("16:00", 200), ("18:00", 200), ("19:00", 400),
    ("20:00", 400), ("09:30", 200), ("12:59", 200), ("10:00-11:00", 200),
], ids=lambda value: str(value))
def test_br01_hour_windows(phase2, monkeypatch, hour, expected):
    status, body = call_booking(monkeypatch, booking_payload(hour=hour))
    assert status == expected
    assert body["success"] is (expected == 200)
    assert [row[4:6] for row in snapshots()] == ([(hour[:5], "booked")] if status == 200 else [])


@pytest.mark.parametrize(("delta", "expected"), [(-1, 200), (0, 400), (1, 400), (3600, 400)])
def test_br01_exact_cutoff(phase2, monkeypatch, delta, expected):
    cutoff = datetime.combine(TODAY, time(3, 30))
    monkeypatch.setattr(BookingClock, "instant", cutoff + timedelta(seconds=delta))
    status, body = call_booking(monkeypatch, booking_payload(day=TODAY, hour="09:00"))
    assert status == expected
    assert body["success"] is (expected == 200)
    assert len(snapshots()) == (expected == 200)


def test_br01_future_date_has_no_today_cutoff(phase2, monkeypatch):
    monkeypatch.setattr(BookingClock, "instant", datetime.combine(TODAY, time(8)))
    status, body = call_booking(monkeypatch, booking_payload(day=TOMORROW, hour="09:00"))
    assert status == 200 and body["success"] is True
    assert snapshots()[0][3:6] == (TOMORROW.isoformat(), "09:00", "booked")


@pytest.mark.parametrize(("hour", "open_period"), [
    ("08:00", False), ("09:00", True), ("13:00", False),
    ("15:00", True), ("19:00", False),
])
@pytest.mark.parametrize("day_kind", ["past", "today-before", "today-at", "future"])
def test_br01_date_and_period_decisions(phase2, monkeypatch, hour, open_period, day_kind, record_property):
    day = {"past": TODAY - timedelta(days=1), "future": TOMORROW}.get(day_kind, TODAY)
    ist_start = datetime.combine(TODAY, time.fromisoformat(hour))
    cutoff = ist_start - timedelta(hours=5, minutes=30)
    monkeypatch.setattr(BookingClock, "instant", cutoff if day_kind == "today-at"
                        else cutoff - timedelta(seconds=1))
    expected = 200 if open_period and day_kind in ("today-before", "future") else 400
    http, body = call_booking(monkeypatch, booking_payload(day=day, hour=hour))
    after = snapshots()
    record_property("decision", f"{day_kind}, {hour}, {open_period}: {http}, {body['message']}")
    assert http == expected
    assert [row[3:6] for row in after] == ([(day.isoformat(), hour, "booked")] if expected == 200 else [])


@pytest.mark.parametrize(("field", "value", "code", "message"), [
    ("appointment_time", "abc", 400, "Invalid appointment time format"),
    ("appointment_time", 900, 400, "Invalid appointment time format"),
    ("notes", 42, 400, "Notes must be text"),
    ("notes", None, 200, "Appointment booked successfully"),
])
def test_br01_booking_field_syntax(phase2, monkeypatch, field, value, code, message):
    status, body = call_booking(monkeypatch, {**booking_payload(), field: value})
    assert status == code and body["success"] is (code == 200)
    assert body["message"] == message
    if code == 200:
        assert snapshots()[0][5:] == ("booked", None)
    else:
        assert snapshots() == []


@pytest.mark.parametrize(("owner", "source", "status"), [
    (owner, source, 404 if owner == "vikram" or source is None else (200 if source == "booked" else 400))
    for owner in ("arjun", "vikram")
    for source in ("booked", "cancelled", "canceled", "completed", "available", None)
])
def test_br03_cancel_transition(phase2, monkeypatch, owner, source, status):
    if source is not None:
        appointment(status=source)
        db.session.commit()
    before = snapshots()
    monkeypatch.setattr(patient, "get_current_user_id", lambda: 4 if owner == "arjun" else 5)
    with app.test_request_context("/api/patient/appointments/1", method="DELETE"):
        result = app.make_response(unwrap(patient.cancel_appointment)(1))
    assert result.status_code == status
    assert result.get_json()["success"] is (status == 200)
    assert snapshots() == ([(*before[0][:5], "cancelled", before[0][6])] if status == 200 else before)


def test_br03_profile_absent(phase2, monkeypatch):
    monkeypatch.setattr(patient, "get_current_user_id", lambda: 999)
    with app.test_request_context("/api/patient/appointments/1", method="DELETE"):
        result = app.make_response(unwrap(patient.cancel_appointment)(1))
    assert result.status_code == 404
    assert result.get_json()["success"] is False
    assert snapshots() == []


@pytest.mark.parametrize(("role", "status"), [("ajay", 403), ("admin", 403), (None, 401)])
@pytest.mark.parametrize("verb", ["post", "delete"])
def test_br04_patient_writes(phase2, role, status, verb):
    client, headers = phase2
    row = appointment()
    db.session.commit()
    before = snapshots()
    if verb == "post":
        result = client.post("/api/patient/appointments", json=booking_payload(), headers=headers.get(role))
    else:
        result = client.delete(f"/api/patient/appointments/{row.id}", headers=headers.get(role))
    assert result.status_code == status
    assert snapshots() == before


@pytest.mark.parametrize(("doctor", "patient"), [(1, 2), (2, 1)])
def test_database_active_slot_uniqueness_preserves_cancelled_history(phase2, doctor, patient):
    cancelled = appointment(status="cancelled")
    booked = appointment()
    db.session.commit()
    assert cancelled.id != booked.id
    before = snapshots()
    with pytest.raises(IntegrityError):
        appointment(doctor=doctor, patient=patient)
    db.session.rollback()
    assert snapshots() == before
