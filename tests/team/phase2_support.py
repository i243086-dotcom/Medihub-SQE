"""Synthetic fixtures shared by the Phase 2 route and browser tests."""

from datetime import date, datetime, time, timedelta

from werkzeug.security import generate_password_hash

from database import db
from models import Appointment, Doctor, DoctorAvailability, Patient, User


class BookingClock(datetime):
    """Freeze the business clock while JWT still uses the real clock."""

    instant = datetime(2030, 1, 15, 2, 30)

    @classmethod
    def utcnow(cls):
        return cls.instant


TODAY = (BookingClock.instant + timedelta(hours=5, minutes=30)).date()
TOMORROW = TODAY + timedelta(days=1)
PAST = TODAY - timedelta(days=1)
BASE_TIME = time(10)
PASSWORD = "synthetic-phase2"
HASH = generate_password_hash(PASSWORD, method="pbkdf2:sha256:1000")
IDENTITIES = {"admin": (1, "admin"), "ajay": (2, "doctor"), "rajesh": (3, "doctor"),
              "arjun": (4, "patient"), "vikram": (5, "patient")}


def seed():
    for username, (user_id, role) in IDENTITIES.items():
        db.session.add(User(id=user_id, username=username, email=username + "@example.test",
                            password_hash=HASH, role=role, is_active=True))
    db.session.add_all([
        Doctor(id=1, user_id=2, name="Ajay Kumar", specialization="Cardiology", is_active=True),
        Doctor(id=2, user_id=3, name="Rajesh Verma", specialization="Neurology", is_active=True),
        Patient(id=1, user_id=4, name="Arjun Patel", is_blacklisted=False),
        Patient(id=2, user_id=5, name="Vikram Singh", is_blacklisted=False),
    ])
    for doctor in (1, 2):
        for offset in range(7):
            for period in ("morning", "evening"):
                availability(doctor, TODAY + timedelta(days=offset), period)
    db.session.commit()


def availability(doctor, day, period="morning", available=True):
    db.session.add(DoctorAvailability(doctor_id=doctor, availability_date=day,
                                      slot_type=period, is_available=available))


def appointment(doctor=1, patient=1, day=TOMORROW, hour=BASE_TIME, status="booked"):
    row = Appointment(doctor_id=doctor, patient_id=patient, appointment_date=day,
                      appointment_time=hour, status=status)
    db.session.add(row)
    db.session.flush()
    return row


def snapshots(*, include_seconds=False):
    time_format = "%H:%M:%S" if include_seconds else "%H:%M"
    db.session.expire_all()
    return [
        (r.id, r.patient_id, r.doctor_id, r.appointment_date.isoformat(),
         r.appointment_time.strftime(time_format), r.status, r.notes)
        for r in db.session.query(Appointment).order_by(Appointment.id)
    ]


def booking_payload(doctor=1, day=TOMORROW, hour="10:00"):
    return {"doctor_id": doctor, "appointment_date": day.isoformat() if isinstance(day, date) else day,
            "appointment_time": hour}
