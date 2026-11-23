"""Execute the specification-derived cases against the real registered Flask routes."""

import json
import os
from pathlib import Path

import pytest
from openapi_schema_validator import OAS30Validator

from database import db
from phase2_support import TODAY, appointment, snapshots


PATH = Path(os.environ.get("MEDIHUB_GENERATED_CASES",
                           Path(__file__).parents[1] / "data/appointment_cases.json"))
DATA = json.loads(PATH.read_text(encoding="utf-8"))
if DATA["clock_date"] != str(TODAY):
    raise ValueError("Generated cases and the frozen fixture clock differ")
ACTORS = {"anonymous": None, "patient": "arjun", "doctor": "ajay", "admin": "admin"}


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda item: item["id"])
def test_generated_contract(phase2, case, record_property):
    client, headers = phase2
    if case["fixture"] == "appointment":
        appointment()
        db.session.commit()
    before = snapshots()
    inputs = case["input"]
    path = case["path"].format(**inputs["path"])
    options = {"headers": headers.get(ACTORS[case["actor"]]), "query_string": inputs["query"]}
    if case["raw_body"] is not None:
        options.update(data=case["raw_body"], content_type="application/json")
    elif case["method"] in {"POST", "PUT"}:
        options["json"] = inputs["body"]

    response = client.open(path, method=case["method"], **options)
    after = snapshots()
    body = response.get_json(silent=True)
    record_property("operation", case["operation"])
    record_property("expected_status", case["expected_status"])
    record_property("actual_status", response.status_code)
    record_property("role", case["actor"])
    record_property("rows_before", json.dumps(before))
    record_property("rows_after", json.dumps(after))
    if response.status_code != case["expected_status"]:
        pytest.fail(f"Expected {case['expected_status']}, got {response.status_code}. DB {before} -> {after}")
    if case["response_schema"]:
        if response.status_code == 405:
            assert response.mimetype == "text/html"
        else:
            assert isinstance(body, dict)
        if case["operation"] == "login" and response.status_code == 200:
            assert body["data"]["token"]
            body = {**body, "data": {"user": body["data"]["user"]}}
        if response.status_code != 405:
            OAS30Validator(case["response_schema"]).validate(body)

    operation = case["operation"]
    if response.status_code != 200 or case["method"] == "GET" or operation == "login":
        assert after == before
    elif operation == "book":
        saved = body["data"]["appointment"]
        assert after == before + [(saved["id"], 1, int(inputs["body"]["doctor_id"]),
                                   inputs["body"]["appointment_date"], inputs["body"]["appointment_time"][:5],
                                   "booked", inputs["body"].get("notes", ""))]
    elif operation == "cancel":
        assert len(after) == 1 and after[0] == (*before[0][:5], "cancelled", before[0][6])
    else:
        request = inputs["body"]
        expected = list(before[0])
        if operation == "adminStatus" and "appointment_date" in request and "appointment_time" in request:
            expected[3:5] = request["appointment_date"], request["appointment_time"][:5]
        for key, index in (("status", 5), ("notes", 6)):
            if key in request:
                expected[index] = request[key]
        assert after == [tuple(expected)]
