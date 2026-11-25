"""Commit appointment writes with controlled handling of a slot collision."""

from sqlite3 import SQLITE_CONSTRAINT_UNIQUE

from sqlalchemy.exc import IntegrityError

from database import db


SLOT_CONFLICT = 'That appointment time conflicts with an existing booking'
SLOT_UNIQUENESS_ERRORS = {
    'UNIQUE constraint failed: appointments.doctor_id, appointments.appointment_date, appointments.appointment_time',
    'UNIQUE constraint failed: appointments.patient_id, appointments.appointment_date, appointments.appointment_time',
}


def commit_appointment():
    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        if (getattr(error.orig, 'sqlite_errorcode', None) != SQLITE_CONSTRAINT_UNIQUE
                or str(error.orig) not in SLOT_UNIQUENESS_ERRORS):
            raise
        return False
    return True
