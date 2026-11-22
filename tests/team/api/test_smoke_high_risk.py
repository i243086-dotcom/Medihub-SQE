"""Stage D: high-risk smoke tests on the isolated in-memory database.

Each test prints the real status code, message and appointments-table rows
(run with -s). A failing assertion means the real behaviour differs from the
expected contract: that is a FINDING to reproduce and report, not a test bug.
"""
from datetime import datetime, timedelta

import pytest

from database import db
from models import Appointment, Doctor

PASSWORDS = {
    "arjun": "arjun",
    "vikram": "vikram",
    "ajay": "ajay.kumar123",
    "admin": "admin",
}


def ist_today():
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()


def apt_date():
    # two days ahead (IST): avoids today's cutoff and stays inside the seeded 7 days
    return (ist_today() + timedelta(days=2)).isoformat()


def login(client, username):
    resp = client.post(
        "/api/auth/login",
        json={"username": username, "password": PASSWORDS[username]},
    )
    assert resp.status_code == 200, resp.get_json()
    return {"Authorization": "Bearer " + resp.get_json()["data"]["token"]}


def first_doctor_id():
    return Doctor.query.order_by(Doctor.id).first().id


def book(client, headers, doctor_id, date, time, **extra):
    body = {"doctor_id": doctor_id, "appointment_date": date, "appointment_time": time}
    body.update(extra)
    return client.post("/api/patient/appointments", json=body, headers=headers)


def table():
    # a failed commit (e.g. unique constraint) leaves the shared session in an
    # error state; roll back so we can read the real stored rows
    db.session.rollback()
    rows = Appointment.query.order_by(Appointment.id).all()
    return [
        (a.id, a.patient_id, a.doctor_id, str(a.appointment_date),
         str(a.appointment_time), a.status)
        for a in rows
    ]


def report(label, resp):
    body = resp.get_json(silent=True)
    print("\n[%s] HTTP %s | body=%s" % (label, resp.status_code, body))
    print("[%s] appointments table = %s" % (label, table()))


def test_d1_book_cancel_rebook_same_slot(client):
    arjun = login(client, "arjun")
    doc, date = first_doctor_id(), apt_date()

    r1 = book(client, arjun, doc, date, "10:00")
    report("D1 book", r1)
    assert r1.status_code == 200
    apt_id = r1.get_json()["data"]["appointment"]["id"]

    r2 = client.delete("/api/patient/appointments/%d" % apt_id, headers=arjun)
    report("D1 cancel", r2)
    assert r2.status_code == 200
    assert table()[0][5] == "cancelled"

    r3 = book(client, arjun, doc, date, "10:00")
    report("D1 rebook same slot", r3)
    # Expected contract: a cancelled slot is free again (slots endpoint and
    # the booking check only treat status='booked' as taken).
    assert r3.status_code == 200
    booked_rows = [t for t in table() if t[5] == "booked"]
    assert len(booked_rows) == 1


def test_d2_cancel_other_patients_appointment(client):
    arjun, vikram = login(client, "arjun"), login(client, "vikram")
    r1 = book(client, arjun, first_doctor_id(), apt_date(), "11:00")
    apt_id = r1.get_json()["data"]["appointment"]["id"]

    r2 = client.delete("/api/patient/appointments/%d" % apt_id, headers=vikram)
    report("D2 wrong-owner cancel", r2)
    assert r2.status_code == 404
    assert table()[0][5] == "booked"  # state unchanged


def test_d3_duplicate_identical_post(client):
    arjun = login(client, "arjun")
    doc, date = first_doctor_id(), apt_date()
    r1 = book(client, arjun, doc, date, "12:00")
    r2 = book(client, arjun, doc, date, "12:00")
    report("D3 first POST", r1)
    report("D3 second identical POST", r2)
    assert r1.status_code == 200
    assert r2.status_code == 400
    assert len(table()) == 1


def _make_cancelled_via_doctor(client):
    arjun, ajay = login(client, "arjun"), login(client, "ajay")
    r = book(client, arjun, first_doctor_id(), apt_date(), "15:00")
    apt_id = r.get_json()["data"]["appointment"]["id"]
    r = client.put("/api/doctor/appointments/%d/status" % apt_id,
                   json={"status": "cancelled"}, headers=ajay)
    assert r.status_code == 200
    return apt_id, ajay


def test_d4a_doctor_reopens_cancelled_appointment(client):
    apt_id, ajay = _make_cancelled_via_doctor(client)
    r = client.put("/api/doctor/appointments/%d/status" % apt_id,
                   json={"status": "booked"}, headers=ajay)
    report("D4a doctor cancelled->booked", r)
    # Expected per BR-03 (to confirm with team): cancelled is terminal.
    assert r.status_code == 400
    assert table()[0][5] == "cancelled"


def test_d4b_admin_sets_arbitrary_status(client):
    arjun, admin = login(client, "arjun"), login(client, "admin")
    r = book(client, arjun, first_doctor_id(), apt_date(), "16:00")
    apt_id = r.get_json()["data"]["appointment"]["id"]
    r = client.put("/api/admin/appointments/%d" % apt_id,
                   json={"status": "banana"}, headers=admin)
    report("D4b admin status='banana'", r)
    assert r.status_code == 400
    assert table()[0][5] == "booked"


@pytest.mark.parametrize("label,kwargs", [
    ("D5a empty JSON object", {"json": {}}),
    ("D5b time 'abc'", {"json": {"doctor_id": 1, "appointment_date": "DATE", "appointment_time": "abc"}}),
    ("D5c time as number 900", {"json": {"doctor_id": 1, "appointment_date": "DATE", "appointment_time": 900}}),
    ("D5d JSON null body", {"data": b"null", "content_type": "application/json"}),
])
def test_d5_malformed_booking_input(client, label, kwargs):
    arjun = login(client, "arjun")
    if "json" in kwargs:
        kwargs["json"] = {k: (apt_date() if v == "DATE" else v) for k, v in kwargs["json"].items()}
    resp = client.post("/api/patient/appointments", headers=arjun, **kwargs)
    report(label, resp)
    assert resp.status_code == 400  # expected: clean validation error, not 500
    assert table() == []
