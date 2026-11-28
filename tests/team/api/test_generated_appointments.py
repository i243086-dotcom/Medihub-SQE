"""Execute the specification-derived cases against the real registered Flask routes."""

import json
import os
from datetime import date, time, timedelta
from pathlib import Path

import pytest
from openapi_schema_validator import OAS30Validator

from database import db
from generated_case_support import setup_generated_case
from phase2_support import TODAY, snapshots


PATH = Path(os.environ.get("MEDIHUB_GENERATED_CASES",
                           Path(__file__).parents[1] / "data/appointment_cases.json"))
DATA = json.loads(PATH.read_text(encoding="utf-8"))
if DATA["clock_date"] != str(TODAY):
    raise ValueError("Generated cases and the frozen fixture clock differ")
ACTORS = {"anonymous": None, "patient": "arjun", "doctor": "ajay", "admin": "admin"}


def check_read_result(operation, inputs, body, before):
    data = body["data"]
    query = inputs["query"]
    if operation == "departments":
        assert {item["name"] for item in data["departments"]} == {"Cardiology", "Neurology"}
    elif operation == "doctors":
        ids = {"Cardiology": 1, "Neurology": 2}
        specialty = query.get("department")
        expected = {ids[specialty]} if specialty in ids else (set() if specialty else {1, 2})
        assert len(data["doctors"]) == len(expected)
        assert {item["id"] for item in data["doctors"]} == expected
    elif operation == "slots":
        day = date.fromisoformat(query["date"])
        doctor_id = int(query["doctor_id"])
        available = doctor_id in (1, 2) and 0 <= (day - TODAY).days < 7
        starts = [9, 10, 11, 12, 15, 16, 17, 18] if available else []
        assert data["doctor_id"] == query["doctor_id"]
        assert data["date"] == query["date"]
        assert [row["appointment_time"] for row in data["slots"]] == [f"{h:02}:00" for h in starts]
        for row, hour in zip(data["slots"], starts):
            start = f"{hour:02}:00"
            assert row["time"] == f"{start}-{hour + 1:02}:00"
            assert row["slot_type"] == ("morning" if hour < 13 else "evening")
            booked = any(r[2:6] == (doctor_id, day.isoformat(), start + ":00", "booked") for r in before)
            assert row["status"] == ("booked" if booked else "available")
    elif operation == "doctorAvailability":
        assert data["doctor"]["id"] == inputs["path"]["doctor_id"]
        assert len(data["availability"]) == (0 if inputs["path"]["doctor_id"] == 2**63 - 1 else 14)
    elif operation in {"patientList", "doctorList", "adminList"}:
        rows = before
        if operation == "patientList":
            rows = [r for r in rows if r[1] == 1]
        elif operation == "doctorList":
            rows = [r for r in rows if r[2] == 1 and r[5] in {"booked", "canceled", "cancelled", "completed"}]
            if query.get("time_filter") == "today":
                rows = [r for r in rows if r[3] == TODAY.isoformat()]
            elif query.get("time_filter") == "upcoming":
                rows = [r for r in rows if r[3] >= TODAY.isoformat() and r[5] == "booked"]
            elif query.get("time_filter") == "completed":
                rows = [r for r in rows if r[5] == "completed"]
            else:
                floor = (TODAY - timedelta(days=30)).isoformat()
                rows = [r for r in rows if r[3] >= floor]
            if query.get("date"):
                rows = [r for r in rows if r[3] == query["date"]]
        if query.get("status"):
            rows = [r for r in rows if r[5] == query["status"]]
        actual = [(a["id"], a["patient_id"], a["doctor_id"], a["status"]) for a in data["appointments"]]
        assert sorted(actual) == sorted((r[0], r[1], r[2], r[5]) for r in rows)


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda item: item["id"])
def test_generated_contract(phase2, case, record_property, monkeypatch):
    client, headers = phase2
    setup_generated_case(case, monkeypatch)
    before = snapshots(include_seconds=True)
    inputs = case["input"]
    path = case["path"].format(**inputs["path"])
    options = {"headers": headers.get(ACTORS[case["actor"]]), "query_string": inputs["query"]}
    if case["raw_body"] is not None:
        options.update(data=case["raw_body"], content_type="application/json")
    elif case["method"] in {"POST", "PUT"}:
        options["json"] = inputs["body"]

    response = client.open(path, method=case["method"], **options)
    after = snapshots(include_seconds=True)
    body = response.get_json(silent=True)
    record_property("operation", case["operation"])
    record_property("expected_status", case["expected_status"])
    record_property("actual_status", response.status_code)
    record_property("role", case["actor"])
    record_property("rows_before", json.dumps(before))
    record_property("rows_after", json.dumps(after))
    if response.status_code != case["expected_status"]:
        pytest.fail(f"Expected {case['expected_status']}, got {response.status_code}. DB {before} -> {after}")
    if response.status_code == 200 and case["method"] == "GET":
        check_read_result(case["operation"], inputs, body, before)
        record_property("content_check", "result values and scoped rows")
    if case["response_schema"]:
        if response.status_code == 405:
            assert response.mimetype == "text/html"
            record_property("response_check", "html-media-type")
        else:
            assert isinstance(body, dict)
        if case["operation"] == "login" and response.status_code == 200:
            assert body["data"]["token"]
            body = {**body, "data": {"user": body["data"]["user"]}}
        if response.status_code != 405:
            OAS30Validator(case["response_schema"]).validate(body)
            record_property("response_check", "json-schema")

    operation = case["operation"]
    if response.status_code != 200 or case["method"] == "GET" or operation == "login":
        assert after == before
    elif operation == "book":
        saved = body["data"]["appointment"]
        start = inputs["body"]["appointment_time"].split("-", 1)[0].strip()
        assert after == before + [(saved["id"], 1, int(inputs["body"]["doctor_id"]),
                                   inputs["body"]["appointment_date"], time.fromisoformat(start).isoformat(),
                                   "booked", inputs["body"].get("notes", ""))]
    elif operation == "cancel":
        assert len(after) == 1 and after[0] == (*before[0][:5], "cancelled", before[0][6])
    else:
        request = inputs["body"]
        expected = list(before[0])
        if operation == "adminStatus" and "appointment_date" in request and "appointment_time" in request:
            expected[3:5] = request["appointment_date"], time.fromisoformat(request["appointment_time"]).isoformat()
        for key, index in (("status", 5), ("notes", 6)):
            if key in request:
                expected[index] = request[key]
        assert after == [tuple(expected)]
