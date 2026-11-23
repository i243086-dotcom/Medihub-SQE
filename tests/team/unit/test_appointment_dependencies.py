"""White-box coverage of roles, availability, treatment and persistence dependencies."""

from datetime import date, time, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app import mail
from database import db
from models import Doctor, DoctorAvailability, Patient, Treatment, User
from phase2_support import PASSWORD, TOMORROW, appointment, availability, snapshots


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
