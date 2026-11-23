"""White-box coverage of roles, availability, treatment and persistence dependencies."""

from datetime import date, datetime, time, timedelta
import sys

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app import app, mail
from database import db
from decorators import get_current_user_role, login_required
from flask_jwt_extended import create_access_token
from flask_sqlalchemy.query import Query
from models import Appointment, Doctor, DoctorAvailability, Patient, Treatment, User
from phase2_support import BookingClock, PASSWORD, TODAY, TOMORROW, appointment, availability, booking_payload, snapshots


@pytest.mark.parametrize(("actor", "path", "verb"), [
    ("arjun", "/api/patient/dashboard", "get"),
    ("arjun", "/api/patient/history", "get"),
    ("arjun", "/api/patient/appointments", "get"),
    ("arjun", "/api/patient/appointments", "post"),
    ("arjun", "/api/patient/appointments/1", "delete"),
    ("ajay", "/api/doctor/dashboard", "get"),
    ("ajay", "/api/doctor/patients", "get"),
    ("ajay", "/api/doctor/patient-history/1", "get"),
    ("ajay", "/api/doctor/appointments", "get"),
    ("ajay", "/api/doctor/appointments/1/status", "put"),
    ("ajay", "/api/doctor/patient-history", "post"),
    ("ajay", "/api/doctor/availability", "get"),
    ("ajay", "/api/doctor/set-slots", "post"),
    ("ajay", "/api/doctor/available-slots", "get"),
])
def test_missing_profile_guards(phase2, actor, path, verb):
    client, headers = phase2
    model = Patient if actor == "arjun" else Doctor
    if model is Doctor:
        DoctorAvailability.query.filter_by(doctor_id=1).delete()
    db.session.delete(db.session.get(model, 1))
    db.session.commit()
    response = client.open(path, method=verb.upper(), headers=headers[actor], json={})
    assert response.status_code == 404
    assert snapshots() == []


@pytest.mark.parametrize("route", ["/api/patient/doctor/availability/1", "/api/patient/doctors"])
def test_inactive_doctor_is_absent(phase2, route):
    client, headers = phase2
    db.session.get(Doctor, 1).is_active = False
    db.session.commit()
    response = client.get(route, headers=headers["arjun"])
    assert (response.status_code == 404 if route.endswith("/1")
            else [item["id"] for item in response.json["data"]["doctors"]] == [2])


def test_admin_blacklist_toggle_round_trip(phase2):
    client, headers = phase2
    route = "/api/admin/patients/1/blacklist"
    for flag in (True, False):
        assert client.put(route, headers=headers["admin"]).status_code == 200
        assert db.session.get(Patient, 1).is_blacklisted is flag
    assert client.put("/api/admin/patients/99/blacklist", headers=headers["admin"]).status_code == 404


def test_admin_doctor_edits_and_deactivation(phase2):
    client, headers = phase2
    auth = headers["admin"]
    route = "/api/admin/doctors/1"
    payload = {"name": "Synthetic Ajay", "specialization": "Cardiology", "experience": 9,
               "qualification": "Synthetic degree", "phone": "000", "is_active": False}
    assert client.put(route, json=payload, headers=auth).status_code == 200
    assert client.put(route, json={}, headers=auth).status_code == 200
    assert db.session.get(Doctor, 1).name == payload["name"]
    assert db.session.get(User, 2).is_active is False
    assert client.delete("/api/admin/doctors/2", headers=auth).status_code == 200
    assert db.session.get(Doctor, 2).is_active is False
    assert client.put("/api/admin/doctors/99", json=payload, headers=auth).status_code == 404
    assert client.delete("/api/admin/doctors/99", headers=auth).status_code == 404


def test_non_active_account_cannot_login(phase2):
    client, _ = phase2
    db.session.get(User, 4).is_active = False
    db.session.commit()
    response = client.post("/api/auth/login", json={"username": "arjun", "password": PASSWORD})
    assert response.status_code == 401
    assert "deactivated" in response.json["message"]


def test_doctor_period_create_and_update(phase2):
    client, headers = phase2
    auth = headers["ajay"]
    day = date.today()
    until = day + timedelta(days=1)
    DoctorAvailability.query.filter(DoctorAvailability.doctor_id == 1,
                                    DoctorAvailability.availability_date.in_((day, until))).delete()
    availability(1, day)
    db.session.commit()
    result = client.post("/api/doctor/set-slots", headers=auth, json={"slots": [
        {"date": day.isoformat(), "slot_type": "morning", "is_available": False},
        {"date": until.isoformat(), "slot_type": "evening", "is_available": True},
    ]})
    assert result.status_code == 200
    assert "1 created, 1 updated" in result.json["message"]
    rows = client.get("/api/doctor/availability", headers=auth).json["data"]["availability"]
    assert len(rows) == 7 and rows[0]["morning_available"] is False and rows[1]["evening_available"] is True
    assert client.post("/api/doctor/set-slots", headers=auth, json={"slots": []}).status_code == 400
    assert snapshots() == []


def test_availability_unique_period(phase2):
    with pytest.raises(IntegrityError):
        availability(1, TOMORROW)
        db.session.flush()
    db.session.rollback()
    assert DoctorAvailability.query.filter_by(doctor_id=1, availability_date=TOMORROW,
                                               slot_type="morning").count() == 1


def test_assigned_doctor_treatment_and_patient_history(phase2):
    client, headers = phase2
    row = appointment()
    db.session.commit()
    path = "/api/doctor/patient-history"
    payload = {"appointment_id": row.id, "diagnosis": "Synthetic diagnosis"}
    assert client.post(path, headers=headers["rajesh"], json=payload).status_code == 404
    assert client.post(path, headers=headers["ajay"], json={}).status_code == 400
    assert Treatment.query.count() == 0
    response = client.post(path, headers=headers["ajay"], json=payload)
    assert response.status_code == 200
    assert snapshots()[0][5] == "completed"
    assert Treatment.query.one().appointment_id == row.id
    history = client.get("/api/patient/history", headers=headers["arjun"]).json["data"]["treatments"]
    assert history[0]["appointment"]["status"] == "completed"
    assert client.get(path + "/99", headers=headers["ajay"]).status_code == 404
    assert client.get(path + "/1", headers=headers["ajay"]).json["appointments"][0]["treatment"]["diagnosis"] == payload["diagnosis"]
    assert client.get("/api/doctor/patients", headers=headers["ajay"]).json["data"]["patients"][0]["id"] == 1


def test_cancellation_email_failure_preserves_commit(phase2, monkeypatch):
    client, headers = phase2
    appointment()
    db.session.commit()

    def fake_failure(_message):
        raise RuntimeError("Synthetic mail error")

    monkeypatch.setattr(mail, "send", fake_failure)
    response = client.delete("/api/patient/appointments/1", headers=headers["arjun"])
    assert response.status_code == 200
    assert snapshots()[0][5] == "cancelled"


def test_legacy_slot_read(phase2):
    client, headers = phase2
    appointment(day=max(date.today(), TOMORROW), hour=time(18), status="available")
    db.session.commit()
    response = client.get("/api/doctor/available-slots", headers=headers["ajay"])
    assert response.json["data"]["slots"][0]["time"] == "18:00"
    assert snapshots()[0][5] == "available"


def test_started_slots_are_omitted(phase2, monkeypatch):
    client, headers = phase2
    monkeypatch.setattr(BookingClock, "instant", datetime.combine(TODAY, time(4)))
    result = client.get("/api/patient/available-slots", headers=headers["arjun"],
                        query_string={"doctor_id": 1, "date": TODAY.isoformat()})
    assert result.status_code == 200
    slots = [row["appointment_time"] for row in result.json["data"]["slots"]]
    assert slots == ["10:00", "11:00", "12:00", "15:00", "16:00", "17:00", "18:00"]
    assert snapshots() == []


@pytest.mark.parametrize("doctor_id", ["1", "0001", 2**63, -2**63-1])
def test_booking_id_storage_range(phase2, doctor_id):
    client, headers = phase2
    result = client.post("/api/patient/appointments", headers=headers["arjun"],
                         json=booking_payload(doctor=doctor_id))
    if isinstance(doctor_id, str):
        assert result.status_code == 200 and snapshots()[0][2] == 1
    else:
        assert result.status_code == 400 and snapshots() == []


def test_booking_decimal_conversion_limit(phase2):
    client, headers = phase2
    limit = sys.get_int_max_str_digits()
    if limit == 0 or limit > 20000:
        pytest.skip("No practical configured CPython decimal conversion limit")
    result = client.post("/api/patient/appointments", headers=headers["arjun"],
                         json=booking_payload(doctor="1" * (limit + 1)))
    assert result.status_code == 400 and snapshots() == []


@pytest.mark.parametrize(("actor", "name"), [
    ("arjun", "Arjun Patel"), ("ajay", "Ajay Kumar"), ("admin", "Administrator"),
    ("orphan", "arjun"), ("missing", None),
])
def test_auth_current_user_profile_mapping(phase2, actor, name):
    client, headers = phase2
    if actor == "orphan":
        db.session.delete(db.session.get(Patient, 1))
        db.session.commit()
        auth = headers["arjun"]
    elif actor == "missing":
        auth = {"Authorization": "Bearer " + create_access_token("999", additional_claims={"role": "patient"})}
    else:
        auth = headers[actor]
    response = client.get("/api/auth/me", headers=auth)
    if name is None:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        assert response.json["data"]["user"]["name"] == name


def test_generic_role_helpers(phase2):
    _, headers = phase2

    @login_required
    def inspect_role():
        return get_current_user_role()

    with app.test_request_context(headers=headers["arjun"]):
        assert inspect_role() == "patient"


@pytest.mark.parametrize(("actor", "route"), [
    ("arjun", "/api/patient/doctors"), ("ajay", "/api/doctor/available-slots"),
])
def test_query_failure_is_reported(phase2, monkeypatch, actor, route):
    client, headers = phase2

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic unavailable database read")

    with monkeypatch.context() as patch:
        patch.setattr(Query, "all", fail)
        response = client.get(route, headers=headers[actor])
    assert response.status_code == 500 and response.json["success"] is False
    assert snapshots() == []


def test_update_availability_failed_commit_rolls_back(phase2, monkeypatch):
    client, headers = phase2
    before = DoctorAvailability.query.count()

    def fail():
        raise RuntimeError("Synthetic failed commit")

    with monkeypatch.context() as patch:
        patch.setattr(db.session, "commit", fail)
        response = client.post("/api/doctor/set-slots", headers=headers["ajay"], json={"slots": [
            {"date": (TOMORROW + timedelta(days=10)).isoformat(), "slot_type": "morning"},
        ]})
    assert response.status_code == 500 and response.json["success"] is False
    assert DoctorAvailability.query.count() == before


def test_doctor_history_without_treatment(phase2):
    client, headers = phase2
    row = appointment()
    db.session.commit()
    response = client.get("/api/doctor/patient-history/1", headers=headers["ajay"])
    result = response.json["appointments"][0]
    assert result["id"] == row.id and result["treatment"] is None


@pytest.mark.parametrize("missing_mail", ["patient", "doctor"])
def test_patient_cancel_with_missing_mail_recipient(phase2, missing_mail):
    client, headers = phase2
    appointment()
    db.session.get(User, 4 if missing_mail == "patient" else 2).email = ""
    db.session.commit()
    response = client.delete("/api/patient/appointments/1", headers=headers["arjun"])
    assert response.status_code == 200
    assert snapshots()[0][5] == "cancelled"


def test_doctor_cancel_skips_missing_patient_mail(phase2):
    client, headers = phase2
    appointment()
    db.session.get(User, 4).email = ""
    db.session.commit()
    result = client.put("/api/doctor/appointments/1/status", headers=headers["ajay"],
                        json={"status": "cancelled"})
    assert result.status_code == 200
    assert snapshots()[0][5] == "cancelled"


def test_model_serialization_of_unassigned_slot(phase2):
    row = appointment(patient=None, status="available")
    db.session.commit()
    assert "patient" not in row.to_dict()
    assert row.to_dict()["doctor"]["id"] == 1
    assert repr(row).startswith("<Appointment ")
    assert repr(db.session.get(Patient, 1)) == "<Patient Arjun Patel>"
    assert repr(db.session.get(Doctor, 1)) == "<Doctor Ajay Kumar>"
    assert repr(DoctorAvailability.query.first()).startswith("<Availability ")
    transient = Appointment(status="available")
    assert "doctor" not in transient.to_dict()


def test_history_of_legacy_record_without_doctor(phase2):
    client, headers = phase2
    row = appointment()
    db.session.add(Treatment(appointment_id=row.id, diagnosis="Synthetic historical result"))
    db.session.flush()
    db.session.execute(text("UPDATE appointments SET doctor_id = 999 WHERE id = :id"), {"id": row.id})
    db.session.commit()
    response = client.get("/api/patient/history", headers=headers["arjun"])
    history = response.json["data"]["treatments"]
    assert history[0]["appointment"]["id"] == row.id
    assert history[0]["doctor"] is None


def test_history_when_related_row_disappears_between_reads(phase2, monkeypatch):
    client, headers = phase2
    row = appointment()
    db.session.add(Treatment(appointment_id=row.id, diagnosis="Synthetic historical result"))
    db.session.commit()
    original = Query.get

    def find(query, key):
        # Simulate a row disappearing after the treatment/appointment join completed.
        if query.column_descriptions[0]["entity"] is Appointment:
            return None
        return original(query, key)

    monkeypatch.setattr(Query, "get", find)
    response = client.get("/api/patient/history", headers=headers["arjun"])
    assert "appointment" not in response.json["data"]["treatments"][0]
