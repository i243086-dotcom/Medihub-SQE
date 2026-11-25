"""Verify the credential transport relevant to the Phase 2 S4502 review."""

import pytest

from app import app, setup_db
from database import db
from models import Patient, User
from phase2_support import PASSWORD, snapshots


WRITES = (
    ("POST", "/api/patient/appointments", "arjun", "admin"),
    ("DELETE", "/api/patient/appointments/<int:appointment_id>", "arjun", "admin"),
    ("POST", "/api/patient/export-history", "arjun", "admin"),
    ("PUT", "/api/patient/profile", "arjun", "admin"),
    ("POST", "/api/admin/doctors", "admin", "arjun"),
    ("PUT", "/api/admin/doctors/<int:doctor_id>", "admin", "arjun"),
    ("DELETE", "/api/admin/doctors/<int:doctor_id>", "admin", "arjun"),
    ("PUT", "/api/admin/appointments/<int:appointment_id>", "admin", "arjun"),
    ("PUT", "/api/admin/patients/<int:patient_id>/blacklist", "admin", "arjun"),
    ("PUT", "/api/admin/patients/<int:patient_id>", "admin", "arjun"),
    ("PUT", "/api/doctor/appointments/<int:appointment_id>/status", "ajay", "arjun"),
    ("POST", "/api/doctor/patient-history", "ajay", "arjun"),
    ("POST", "/api/doctor/set-slots", "ajay", "arjun"),
    ("PUT", "/api/doctor/profile", "ajay", "arjun"),
)
PUBLIC = {("POST", "/api/auth/" + route) for route in ("login", "register", "logout")}


def row_counts():
    return {
        table.name: db.session.scalar(db.select(db.func.count()).select_from(table))
        for table in db.metadata.sorted_tables
    }


def test_write_route_inventory_requires_explicit_review():
    actual = {
        (method, rule.rule)
        for rule in app.url_map.iter_rules()
        for method in rule.methods & {"POST", "PUT", "PATCH", "DELETE"}
    }
    assert actual == PUBLIC | {(method, path) for method, path, *_ in WRITES}
    assert app.config["JWT_TOKEN_LOCATION"] == ["headers"]


@pytest.mark.parametrize("method,rule,role,wrong_role", WRITES)
def test_protected_write_requires_header(phase2, method, rule, role, wrong_role, record_property):
    client, headers = phase2
    path = rule
    for name in ("doctor_id", "patient_id", "appointment_id"):
        path = path.replace(f"<int:{name}>", "1")
    before = row_counts(), snapshots(include_seconds=True)
    client.set_cookie(app.config["JWT_ACCESS_COOKIE_NAME"], headers[role]["Authorization"].split(" ", 1)[1])
    response = client.open(path, method=method, json={})
    assert response.status_code == 401
    assert response.get_json()["msg"] == "Missing Authorization Header"
    assert not response.headers.getlist("Set-Cookie")
    assert (row_counts(), snapshots(include_seconds=True)) == before

    # The same cookie cannot override the role authenticated by the header.
    response = client.open(path, method=method, json={}, headers=headers[wrong_role])
    assert response.status_code == 403
    assert (row_counts(), snapshots(include_seconds=True)) == before
    record_property("credential_transport", "valid cookie only: 401; wrong-role header plus valid cookie: 403")


@pytest.mark.parametrize("path,form_status", [("/api/auth/login", 400), ("/api/auth/register", 415)])
def test_public_auth_rejects_form_encoding(phase2, path, form_status):
    client, _ = phase2
    before = row_counts()
    response = client.post(path, data={"username": "phase2-review", "password": PASSWORD})
    assert response.status_code == form_status
    assert not response.headers.getlist("Set-Cookie")
    assert row_counts() == before


def test_public_login_returns_token_only_in_json(phase2):
    client, _ = phase2
    before = row_counts()
    response = client.post("/api/auth/login", json={"username": "arjun", "password": PASSWORD})
    assert response.status_code == 200
    assert not response.headers.getlist("Set-Cookie")
    token = response.get_json()["data"]["token"]
    assert isinstance(token, str) and token
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer " + token}).status_code == 200
    assert client.get("/api/auth/me").status_code == 401
    assert row_counts() == before


def test_public_registration_does_not_create_authenticated_session(phase2):
    client, _ = phase2
    payload = {"username": "phase2-review", "password": PASSWORD,
               "name": "Phase Two Review", "email": "phase2-review@example.test"}
    before = row_counts()
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    assert not response.headers.getlist("Set-Cookie")
    assert "token" not in response.get_json()["data"]
    assert client.get("/api/auth/me").status_code == 401
    assert row_counts() == {**before, "users": before["users"] + 1, "patients": before["patients"] + 1}
    assert User.query.filter_by(username=payload["username"], role="patient").one().patient is not None


def test_public_logout_does_not_mutate_server_session_or_database(phase2):
    client, _ = phase2
    before = row_counts(), snapshots(include_seconds=True)
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert not response.headers.getlist("Set-Cookie")
    assert (row_counts(), snapshots(include_seconds=True)) == before


@pytest.mark.parametrize("path,method", [
    ("/api/auth/login", "POST"),
    ("/api/auth/register", "POST"),
    ("/api/patient/appointments", "POST"),
    ("/api/doctor/appointments/1/status", "PUT"),
    ("/api/admin/appointments/1", "PUT"),
])
def test_cross_origin_preflight_grants_no_cors_access(phase2, path, method):
    client, _ = phase2
    response = client.options(path, headers={
        "Origin": "https://review.example.invalid",
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    assert response.status_code in (200, 204)
    assert not response.headers.get("Access-Control-Allow-Origin")
    assert not response.headers.get("Access-Control-Allow-Credentials")


def test_bootstrap_requires_explicit_admin_password(phase2, monkeypatch):
    assert Patient.query.count() == 2
    User.query.filter_by(role="admin").delete()
    db.session.commit()
    monkeypatch.delenv("MEDIHUB_INITIAL_ADMIN_PASSWORD", raising=False)
    setup_db()
    assert User.query.filter_by(role="admin").count() == 0
    monkeypatch.setenv("MEDIHUB_INITIAL_ADMIN_PASSWORD", PASSWORD)
    setup_db()
    assert User.query.filter_by(role="admin").count() == 1
    client, _ = phase2
    assert client.post("/api/auth/login", json={"username": "admin", "password": PASSWORD}).status_code == 200
