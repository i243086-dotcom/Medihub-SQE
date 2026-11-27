"""Record normal role and ownership decisions through the isolated MediHub browser."""

import json
import os
from pathlib import Path

import pytest
from playwright.sync_api import expect

from database import db
from e2e.test_appointment_flows import assets, browser_app, confirm, doctor_list, login, patient_list, select_doctor, slot
from phase2_support import TOMORROW, appointment, booking_payload, snapshots


@pytest.fixture()
def page(browser):
    proxy = os.environ["MEDIHUB_PHASE4_PROXY"]
    assert proxy == "http://127.0.0.1:8093"
    context = browser.new_context(viewport={"width": 1440, "height": 1000},
                                  proxy={"server": proxy, "bypass": "<-loopback>"})
    try:
        yield context.new_page()
    finally:
        context.close()


def save(case, page, response, before, after, user, expected, observation):
    root = Path(os.environ["MEDIHUB_PHASE4_EVIDENCE"])
    body = response.json()
    evidence = {
        "test": case, "account": user, "expected_status": expected, "http_status": response.status,
        "method": response.request.method, "url": response.url,
        "browser_observation": observation, "response_message": body.get("message") or body.get("msg"),
        "bearer_present": (response.request.header_value("authorization") or "").startswith("Bearer "),
        "response_set_cookie": response.header_value("set-cookie") is not None,
        "before": before, "after": after,
    }
    (root / f"{case}.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf8")
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=root / "screenshots" / f"{case}.png", full_page=True, animations="disabled")


def call(page, path, method, payload=None):
    with page.expect_response(lambda r: r.url.endswith(path) and r.request.method == method) as response:
        page.evaluate("([path, method, payload]) => callAPI(path.slice(4), method, payload)", [path, method, payload])
    return response.value


def test_p4_01_patient_booking(browser_app, page):
    before = snapshots()
    login(page, browser_app)
    date = select_doctor(page)
    date.fill(TOMORROW.isoformat())
    slot(page, "10:00 AM").click()
    with page.expect_response(lambda r: r.url.endswith("/api/patient/appointments") and r.request.method == "POST") as r:
        confirm(page).click()
    expect(page.get_by_text("Appointment booked successfully!", exact=True)).to_be_visible()
    after = snapshots()
    assert len(after) == 1 and after[0][1:6] == (1, 1, TOMORROW.isoformat(), "10:00", "booked")
    assert r.value.status == 200
    save("P4-01", page, r.value, before, after, "arjun", 200, "Booking confirmation visible")


def test_p4_03_patient_cancellation(browser_app, page):
    row = appointment()
    db.session.commit()
    before = snapshots()
    login(page, browser_app)
    patient_list(page).filter(has_text="Ajay Kumar").get_by_title("Cancel Appointment").click()
    with page.expect_response(lambda r: r.url.endswith(f"/api/patient/appointments/{row.id}") and r.request.method == "DELETE") as r:
        page.get_by_role("button", name="Yes, Cancel Appointment").click()
    expect(page.get_by_text("Appointment cancelled successfully", exact=True)).to_be_visible()
    expect(page.locator("#patient-appointments").get_by_text("Cancelled", exact=True)).to_be_visible()
    after = snapshots()
    assert r.value.status == 200
    assert after == [(*before[0][:5], "cancelled", before[0][6])]
    save("P4-03", page, r.value, before, after, "arjun", 200, "Cancellation confirmation and Cancelled row visible")


@pytest.mark.parametrize("case,user,method,expected", [
    ("P4-02", "ajay", "POST", 403),
    ("P4-04", "ajay", "DELETE", 403),
    ("P4-05", "vikram", "DELETE", 404),
    ("P4-06", None, "POST", 401),
], ids=["doctor-book", "doctor-cancel", "other-patient-cancel", "anonymous-book"])
def test_denied_access(browser_app, page, case, user, method, expected):
    path = "/api/patient/appointments"
    if method == "DELETE":
        path += f"/{appointment().id}"
        db.session.commit()
    before = snapshots()
    if user:
        login(page, browser_app, user=user)
    else:
        page.goto(browser_app)
    response = call(page, path, method, booking_payload() if method == "POST" else None)
    after = snapshots()
    assert response.status == expected and after == before
    message = response.json().get("message") or response.json().get("msg")
    assert message == {403: "Patient access only", 404: "Appointment not found", 401: "Missing Authorization Header"}[expected]
    save(case, page, response, before, after, user or "anonymous", expected,
         "Browser API response asserted. Screenshot shows the actual account screen.")


def test_p4_07_assigned_doctor_readback(browser_app, page):
    appointment(status="cancelled")
    appointment(doctor=2)
    db.session.commit()
    before = snapshots()
    with page.expect_response(lambda r: "/api/doctor/appointments" in r.url and r.request.method == "GET") as r:
        login(page, browser_app, user="ajay")
    rows = doctor_list(page)
    response = r.value
    expect(rows.filter(has_text="Arjun Patel").get_by_text("Cancelled", exact=True)).to_be_visible()
    after = snapshots()
    assert response.status == 200 and after == before
    assert [apt["id"] for apt in response.json()["data"]["appointments"]] == [before[0][0]]
    save("P4-07", page, response, before, after, "ajay", 200, "Only assigned appointment returned, Cancelled visible")


def test_p4_transport_headers(browser_app, page):
    with page.expect_response(lambda r: r.url.endswith("/api/auth/login") and r.request.method == "POST") as r:
        login(page, browser_app)
    assert r.value.status == 200 and r.value.header_value("set-cookie") is None
    assert page.evaluate("Boolean(localStorage.getItem('token'))")
    assert not page.context.cookies()
    destination = f"{browser_app}/api/patient/appointments"
    preflight = page.request.fetch(destination, method="OPTIONS", headers={
        "Origin": "https://untrusted.example.test",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization, content-type",
    })
    assert preflight.status == 200
    assert not any(name.startswith("access-control-allow-") for name in preflight.headers)
    root = Path(os.environ["MEDIHUB_PHASE4_EVIDENCE"])
    (root / "transport.json").write_text(json.dumps({
        "login_http": r.value.status, "login_set_cookie": False, "browser_cookie_count": 0,
        "local_storage_token_present": True, "preflight_http": preflight.status,
        "origin_test_value": "https://untrusted.example.test", "cors_allow_headers": [],
    }, indent=2) + "\n", encoding="utf8")
