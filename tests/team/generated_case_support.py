"""Fixtures for generated appointment probes, separate from the reviewed auth fixtures."""

from datetime import date, datetime, time, timedelta

from database import db
from models import Doctor, User
from phase2_support import BookingClock, TODAY, appointment
from routes import doctor


class FilterClock(date):
    @classmethod
    def today(cls):
        return TODAY


def setup_generated_case(case, monkeypatch):
    monkeypatch.setattr(doctor, "date", FilterClock)
    if case.get("clock"):
        monkeypatch.setattr(BookingClock, "instant", datetime.fromisoformat(case["clock"]))
    fixture = case["fixture"]
    if fixture == "appointment":
        appointment()
    elif fixture == "inactive-account":
        User.query.filter_by(username="arjun").one().is_active = False
    elif fixture in {"patient-list", "doctor-list"}:
        appointment(day=TODAY, hour=time(9))
        appointment(hour=time(10), status="cancelled")
        appointment(hour=time(11), status="completed")
        appointment(hour=time(12), status="canceled")
        appointment(hour=time(15), status="available")
        if fixture == "patient-list":
            appointment(patient=2, hour=time(16))
        else:
            appointment(patient=2, doctor=2, hour=time(16))
            appointment(patient=2, hour=time(17))
            for offset in (-31, -30, -29):
                appointment(day=TODAY + timedelta(days=offset), hour=time(10))
    elif fixture == "slots":
        appointment()
    elif fixture == "maximum-doctor":
        user = User(username="max-doctor", email="max-doctor@example.test",
                    password_hash="unused", role="doctor", is_active=True)
        db.session.add(user)
        db.session.flush()
        db.session.add(Doctor(id=2**63 - 1, user_id=user.id, name="Maximum ID Doctor",
                              specialization="Boundary", is_active=True))
    db.session.commit()
