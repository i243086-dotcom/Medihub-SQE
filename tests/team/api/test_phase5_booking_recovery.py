"""Phase 5 integration test for exactly-once recovery of an interrupted booking."""

import json
import os
from pathlib import Path
import sqlite3

from sqlalchemy import event
from sqlalchemy.exc import OperationalError

from app import app
from database import db
from phase2_support import booking_payload


QUERY = ("SELECT id, patient_id, doctor_id, appointment_date, appointment_time, status "
         "FROM appointments ORDER BY id")
ROUTE = "/api/patient/appointments"


def read_rows(connection):
    return [dict(row) for row in connection.exec_driver_sql(QUERY).mappings()]


def persisted_rows():
    with db.engine.connect() as connection:
        return read_rows(connection)


def test_booking_recovers_after_database_commit_dependency_failure(phase2):
    client, tokens = phase2
    payload = booking_payload()
    headers = tokens["arjun"]
    evidence = {"operation": f"POST {ROUTE}", "payload": payload, "engine": str(db.engine.url),
                "sqlite_version": sqlite3.sqlite_version, "before": persisted_rows()}

    def fail_after_insert(session):
        session.flush()
        evidence["uncommitted"] = read_rows(session.connection())
        raise OperationalError(None, None, sqlite3.OperationalError("synthetic commit dependency unavailable"))

    try:
        assert evidence["before"] == []
        # Each scenario makes a separate Flask app context to exercise the normal
        # scoped-session teardown, including rollback after the failed request.
        with app.app_context():
            session = db.session()
            event.listen(session, "before_commit", fail_after_insert)
            try:
                response = client.post(ROUTE, json=payload, headers=headers)
            finally:
                event.remove(session, "before_commit", fail_after_insert)
        evidence["failure_response"] = {"status": response.status_code, "body": response.get_json()}
        evidence["after_failure"] = persisted_rows()
        assert len(evidence["uncommitted"]) == 1, "Fault must follow a real SQLite INSERT"
        uncommitted, = evidence["uncommitted"]
        assert uncommitted["patient_id"] == 1 and uncommitted["doctor_id"] == payload["doctor_id"]
        assert evidence["failure_response"] == {
            "status": 500, "body": {"success": False, "message": "Internal server error"}}
        assert evidence["after_failure"] == evidence["before"]

        with app.app_context():
            retry = client.post(ROUTE, json=payload, headers=headers)
        reply = retry.get_json()
        evidence["retry_response"] = {"status": retry.status_code, "message": reply["message"]}
        evidence["after_retry"] = persisted_rows()
        assert retry.status_code == 200 and reply["success"]
        assert len(evidence["after_retry"]) == 1
        row, = evidence["after_retry"]
        assert row == {**uncommitted, "id": reply["data"]["appointment"]["id"]}
        assert row["appointment_date"] == payload["appointment_date"]
        assert row["appointment_time"] == "10:00:00.000000"
        assert row["status"] == "booked"

        with app.app_context():
            duplicate = client.post(ROUTE, json=payload, headers=headers)
            listing = client.get(ROUTE, headers=headers)
        appointments = listing.get_json()["data"]["appointments"]
        evidence["duplicate_response"] = {"status": duplicate.status_code, "body": duplicate.get_json()}
        evidence["readback"] = {"status": listing.status_code, "appointment_ids": [a["id"] for a in appointments]}
        evidence["after_duplicate"] = persisted_rows()
        assert duplicate.status_code == 400
        assert not duplicate.get_json()["success"]
        assert listing.status_code == 200 and evidence["readback"]["appointment_ids"] == [row["id"]]
        assert evidence["after_duplicate"] == [row]
    finally:
        destination = os.environ.get("MEDIHUB_P5_RECOVERY_EVIDENCE")
        if destination:
            Path(destination).write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
