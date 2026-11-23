"""Six MediHub use cases, with one normal and four varied flows each."""

from datetime import datetime, time, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from threading import Thread
import os
import re

import pytest
from playwright.sync_api import expect
from werkzeug.serving import make_server

from app import app
from database import db
from models import Doctor
from phase2_support import BookingClock, PASSWORD, TODAY, TOMORROW, appointment, snapshots


ASSETS = {
    "https://unpkg.com/vue@3/dist/vue.global.js": ("vue.global.js", "application/javascript",
        "0f9a092ad87f4e7a2b37c3fb5aa425b34dcd6ceef24070baf0d05e54353e980c"),
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js": (
        "bootstrap.bundle.min.js", "application/javascript",
        "aa53d582f97eb594c2a5cc5824574707f9ba9837bce3046bfa5f3556860f4e04"),
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css": (
        "bootstrap.min.css", "text/css",
        "7f1d37f0d90b6385354c2ac10e2bb91563c46bd7a266ed351222ebcac8496c2a"),
}


@pytest.fixture(scope="session")
def assets():
    asset_dir = os.environ.get("MEDIHUB_BROWSER_ASSETS")
    if not asset_dir:
        pytest.fail("Set MEDIHUB_BROWSER_ASSETS to the folder containing verified Vue and Bootstrap assets")
    root = Path(asset_dir)
    for filename, _, digest in ASSETS.values():
        assert sha256((root / filename).read_bytes()).hexdigest() == digest, filename
    return root


@pytest.fixture()
def browser_app(phase2, page, assets):
    if str(db.engine.url) != "sqlite://":
        pytest.fail("Refusing to start browser tests without disposable SQLite")
    server = make_server("127.0.0.1", 5001, app)
    thread = Thread(target=server.serve_forever, daemon=True)
    url = "http://127.0.0.1:5001"

    def route_request(route):
        url_requested = route.request.url
        if url_requested.startswith(url + "/"):
            route.continue_()
        elif url_requested in ASSETS:
            name, kind, _ = ASSETS[url_requested]
            route.fulfill(path=assets / name, content_type=kind)
        else:
            route.abort()

    page.route("**/*", route_request)
    page.clock.set_fixed_time(BookingClock.instant.replace(tzinfo=timezone.utc))
    thread.start()
    try:
        yield url
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def login(page, url, user="arjun"):
    page.goto(url, wait_until="domcontentloaded")
    page.get_by_role("button", name="Sign In", exact=True).first.click()
    page.get_by_placeholder("Enter your username").fill(user)
    page.locator("input[type=password]").fill(PASSWORD)
    page.locator("form button[type=submit]").click()
    expect(page.get_by_role("button", name="Logout")).to_be_visible()


def specialization(page, name="Cardiology"):
    page.get_by_role("tab", name="Book Appointment").click()
    page.get_by_text(name, exact=True).click()
    expect(page.get_by_text("Select a doctor from the list")).to_be_visible()


def select_doctor(page):
    specialization(page)
    page.get_by_text("Dr. Ajay Kumar", exact=True).click()
    return page.locator("#book input[type=date]")


def confirm(page):
    return page.get_by_role("button", name="Confirm Booking")


def slot(page, start):
    return page.get_by_role("button", name=re.compile(rf"^{re.escape(start)} "))


def patient_list(page):
    page.get_by_role("tab", name="My Appointments").click()
    return page.locator("#patient-appointments").get_by_role("row")


def doctor_list(page):
    page.get_by_role("tab", name="Appointments", exact=True).click()
    return page.locator("#doctor-appointments").get_by_role("row")


def flow_ids(case, names):
    return [pytest.param(name, id=f"{case}-{label}")
            for name, label in zip(names, ("N", "A1", "A2", "E1", "E2"), strict=True)]


@pytest.mark.parametrize("flow", flow_ids("UC01", ["primary", "alternate", "profile", "inactive", "no-selection"]))
def test_uc01_discover_doctor(browser_app, page, flow):
    if flow == "inactive":
        db.session.get(Doctor, 2).is_active = False
        db.session.commit()
    login(page, browser_app)
    page.get_by_role("tab", name="Book Appointment").click()
    expect(page.get_by_text("Choose a specialization to get started")).to_be_visible()
    if flow == "inactive":
        expect(page.get_by_text("Neurology", exact=True)).to_have_count(0)
        expect(page.get_by_text("Cardiology", exact=True)).to_be_visible()
    elif flow == "no-selection":
        expect(confirm(page)).to_be_disabled()
        expect(page.locator("#book input[type=date]")).to_have_count(0)
    else:
        specialty, doctor = ("Neurology", "Rajesh Verma") if flow == "alternate" else ("Cardiology", "Ajay Kumar")
        specialization(page, specialty)
        expect(page.get_by_text("Dr. " + doctor, exact=True)).to_be_visible()
        if flow == "profile":
            page.get_by_role("button", name="Profile", exact=True).click()
            modal = page.locator("#doctorProfileModal")
            expect(modal.get_by_text("Doctor Profile", exact=True)).to_be_visible()
            modal.get_by_role("button", name="Book Appointment").click()
        else:
            page.get_by_text("Dr. " + doctor, exact=True).click()
        expect(page.locator("#book input[type=date]")).to_be_visible()
    assert snapshots() == []


@pytest.mark.parametrize("flow", flow_ids("UC02", ["tomorrow", "today", "last-seeded", "outside-seed", "yesterday"]))
def test_uc02_schedule_date(browser_app, page, flow):
    login(page, browser_app)
    date_input = select_doctor(page)
    dates = {"tomorrow": TOMORROW, "today": TODAY, "last-seeded": TODAY + timedelta(days=6),
             "outside-seed": TODAY + timedelta(days=7), "yesterday": TODAY - timedelta(days=1)}
    expect(date_input).to_have_attribute("min", TODAY.isoformat())
    date_input.fill(dates[flow].isoformat())
    if flow in {"outside-seed", "yesterday"}:
        expect(page.get_by_text("No slots available for this date.")).to_be_visible()
        expect(confirm(page)).to_be_disabled()
        assert date_input.evaluate("el => el.validity.rangeUnderflow") == (flow == "yesterday")
    else:
        expect(slot(page, "09:00 AM")).to_be_enabled()
        expect(slot(page, "03:00 PM")).to_be_enabled()
    assert snapshots() == []


@pytest.mark.parametrize("flow", flow_ids("UC03", ["morning-note", "evening", "no-note", "occupied", "stale-slot"]))
def test_uc03_submit_booking(browser_app, page, flow):
    booked_time = time(9)
    if flow == "occupied":
        appointment(patient=2, hour=booked_time)
        db.session.commit()
    login(page, browser_app)
    select_doctor(page).fill(TOMORROW.isoformat())
    if flow == "occupied":
        expect(slot(page, "09:00 AM")).to_be_disabled()
        expect(confirm(page)).to_be_disabled()
        assert snapshots()[0][1:6] == (2, 1, TOMORROW.isoformat(), "09:00", "booked")
        return
    start, stored = {"evening": ("03:00 PM", "15:00"), "no-note": ("10:00 AM", "10:00")}.get(flow, ("09:00 AM", "09:00"))
    slot(page, start).click()
    note = "Synthetic visit note" if flow == "morning-note" else ""
    if note:
        page.locator("#book textarea").fill(note)
    if flow == "stale-slot":
        appointment(patient=2, hour=booked_time)
        db.session.commit()
    before = snapshots()
    confirm(page).click()
    if flow == "stale-slot":
        expect(page.get_by_text(re.compile("slot is already booked", re.I))).to_be_visible()
        assert snapshots() == before
    else:
        expect(page.get_by_text("Appointment booked successfully!")).to_be_visible()
        assert len(snapshots()) == 1
        assert snapshots()[0][1:] == (1, 1, TOMORROW.isoformat(), stored, "booked", note)


@pytest.mark.parametrize("flow", flow_ids("UC04", ["booked", "mixed", "details", "empty", "other-owner"]))
def test_uc04_patient_appointment_list(browser_app, page, flow):
    if flow == "other-owner":
        appointment(patient=2)
    elif flow in {"booked", "mixed", "details"}:
        appointment(status="cancelled" if flow == "details" else "booked")
        if flow == "mixed":
            appointment(doctor=2, hour=time(15), status="cancelled")
    db.session.commit()
    before = snapshots()
    login(page, browser_app)
    rows = patient_list(page)
    if flow in {"empty", "other-owner"}:
        expect(page.get_by_text("No appointments found")).to_be_visible()
        expect(rows.filter(has_text="Ajay Kumar")).to_have_count(0)
    else:
        row = rows.filter(has_text="Ajay Kumar")
        expect(row.get_by_text("Cancelled" if flow == "details" else "Booked", exact=True)).to_be_visible()
        if flow == "mixed":
            expect(rows.filter(has_text="Rajesh Verma").get_by_text("Cancelled", exact=True)).to_be_visible()
        elif flow == "details":
            row.get_by_title("View Details").click()
            expect(page.get_by_text("Appointment History Details")).to_be_visible()
    assert snapshots() == before


@pytest.mark.parametrize("flow", flow_ids("UC05", ["cancel", "keep", "close", "cancelled", "completed"]))
def test_uc05_cancel_appointment(browser_app, page, flow):
    state = flow if flow in {"cancelled", "completed"} else "booked"
    appointment(status=state)
    db.session.commit()
    before = snapshots()
    login(page, browser_app)
    row = patient_list(page).filter(has_text="Ajay Kumar")
    expect(row.get_by_text(state.capitalize(), exact=True)).to_be_visible()
    if state != "booked":
        expect(row.get_by_title("Cancel Appointment")).to_have_count(0)
    else:
        row.get_by_title("Cancel Appointment").click()
        dialog = page.locator("#cancelAppointmentModal")
        expect(dialog).to_be_visible()
        label = {"cancel": "Yes, Cancel Appointment", "keep": "No, Keep it", "close": "Close"}[flow]
        dialog.get_by_role("button", name=label).click()
        expect(dialog).to_be_hidden()
        if flow == "cancel":
            expect(page.get_by_text("Appointment cancelled successfully", exact=True)).to_be_visible()
            expect(row.get_by_text("Cancelled", exact=True)).to_be_visible()
            assert snapshots() == [(*before[0][:5], "cancelled", before[0][6])]
            return
        expect(row.get_by_text("Booked", exact=True)).to_be_visible()
    assert snapshots() == before


@pytest.mark.parametrize("flow", flow_ids("UC06", ["read-cancelled", "read-booked", "read-completed", "wrong-doctor", "no-booking-action"]))
def test_uc06_doctor_readback(browser_app, page, flow):
    state = {"read-booked": "booked", "read-completed": "completed"}.get(flow, "cancelled")
    if flow == "read-cancelled":
        appointment()
        db.session.commit()
        login(page, browser_app)
        patient_list(page).filter(has_text="Ajay Kumar").get_by_title("Cancel Appointment").click()
        page.get_by_role("button", name="Yes, Cancel Appointment").click()
        expect(page.get_by_text("Appointment cancelled successfully", exact=True)).to_be_visible()
        page.get_by_role("button", name="Logout").click()
    else:
        appointment(status=state)
        db.session.commit()
    before = snapshots()
    assert before[0][5] == state
    login(page, browser_app, "rajesh" if flow == "wrong-doctor" else "ajay")
    row = doctor_list(page).filter(has_text="Arjun Patel")
    if flow == "wrong-doctor":
        expect(page.get_by_role("heading", name="No Appointments")).to_be_visible()
        expect(row).to_have_count(0)
    else:
        expect(row.get_by_text(state.capitalize(), exact=True)).to_be_visible()
        if flow == "no-booking-action":
            expect(page.get_by_role("tab", name="Book Appointment")).to_have_count(0)
    assert snapshots() == before
