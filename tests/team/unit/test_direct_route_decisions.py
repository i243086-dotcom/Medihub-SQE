"""Invoke business handlers directly to isolate their decisions from HTTP routing."""

import json
import sys
from datetime import time
from inspect import unwrap
from pathlib import Path

import pytest
from werkzeug.exceptions import MethodNotAllowed, NotFound

from app import app
from database import db
from generated_case_support import setup_generated_case
from phase2_support import TOMORROW, appointment, snapshots


ACTORS = {"anonymous": None, "patient": 4, "doctor": 2, "admin": 1}
DATA = json.loads((Path(__file__).parents[1] / "data/appointment_cases.json").read_text(encoding="utf-8"))


def direct_cases():
    routes = app.url_map.bind("127.0.0.1")
    for case in DATA["cases"]:
        if case["probe"] == "role":
            continue
        path = case["path"].format(**case["input"]["path"])
        try:
            endpoint, parameters = routes.match(path, method=case["method"])
        except (MethodNotAllowed, NotFound):
            continue
        if not endpoint.startswith(("auth.", "patient.", "doctor.", "admin.")):
            continue
        yield pytest.param(case, endpoint, parameters, id="WBU-" + case["id"])


@pytest.mark.parametrize(("case", "endpoint", "parameters"), list(direct_cases()))
def test_direct_handler_decision(phase2, monkeypatch, case, endpoint, parameters):
    setup_generated_case(case, monkeypatch)
    before = snapshots()
    handler = unwrap(app.view_functions[endpoint])
    module = sys.modules[handler.__module__]
    if hasattr(module, "get_current_user_id"):
        monkeypatch.setattr(module, "get_current_user_id", lambda: ACTORS[case["actor"]])
    options = {"query_string": case["input"]["query"]}
    if case["raw_body"] is not None:
        options.update(data=case["raw_body"], content_type="application/json")
    elif case["method"] in {"POST", "PUT"}:
        options["json"] = case["input"]["body"]
    path = case["path"].format(**case["input"]["path"])
    with app.test_request_context(path, method=case["method"], **options):
        response = app.make_response(handler(**parameters))
    assert response.status_code == case["expected_status"]
    assert response.json["success"] is (response.status_code == 200)
    after = snapshots()
    if response.status_code != 200 or case["method"] == "GET" or case["operation"] == "login":
        assert after == before
    elif "appointment" in response.json["data"]:
        returned = response.json["data"]["appointment"]
        assert any(row[0] == returned["id"] and row[5] == returned["status"] for row in after)
    else:
        assert len(after) == 1 and after[0][5] == "cancelled"


@pytest.mark.parametrize(("actor", "path", "state"), [
    ("arjun", "/api/patient/dashboard", 200),
    ("ajay", "/api/doctor/dashboard", 200),
    ("arjun", "/api/admin/appointments", 403),
    ("arjun", "/api/doctor/dashboard", 403),
    ("ajay", "/api/patient/departments", 403),
])
def test_dashboard_and_role_branches(phase2, actor, path, state):
    client, headers = phase2
    appointment()
    db.session.commit()
    before = snapshots()
    result = client.get(path, headers=headers[actor])
    assert result.status_code == state
    assert result.json["success"] is (state == 200)
    assert snapshots() == before


def test_admin_conflicting_reschedule_handler(phase2):
    client, headers = phase2
    appointment()
    appointment(patient=2, hour=time(11))
    db.session.commit()
    before = snapshots()
    result = client.put("/api/admin/appointments/1", json={"appointment_date": TOMORROW.isoformat(),
                        "appointment_time": "11:00"}, headers=headers["admin"])
    assert result.status_code == 400 and snapshots() == before


def test_authenticated_logout_route(phase2):
    client, headers = phase2
    response = client.post("/api/auth/logout", headers=headers["arjun"])
    assert response.status_code == 200 and response.json["success"] is True
