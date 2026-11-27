"""Phase 3 real booking rejection, keyboard submission and recovery."""

from datetime import time
from pathlib import Path
import os
import re

from playwright.sync_api import expect

from database import db
from phase2_support import TOMORROW, appointment, snapshots
from e2e.test_appointment_flows import assets, browser_app, confirm, login, select_doctor, slot


def evidence(page, name):
    root = Path(os.environ['MEDIHUB_PHASE3_SHOTS'])
    root.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=root / f'{name}.png', animations='disabled')


def tab_to(page, control, limit=16):
    for _ in range(limit):
        page.keyboard.press('Tab')
        if control.evaluate('el => el === document.activeElement'):
            break
    expect(control).to_be_focused()


def test_phase3_booking_rejection_keyboard_submission_and_recovery(browser_app, page):
    login(page, browser_app)
    if os.environ.get('MEDIHUB_PHASE3_FIXED') == '1':
        page.locator('#book-tab').focus()
        specialty = page.get_by_role('button', name=re.compile('Cardiology'))
        tab_to(page, specialty)
        evidence(page, 'booking-specialty-focus')
        page.keyboard.press('Enter')
        doctor = page.get_by_role('button', name=re.compile('Select Dr. Ajay Kumar'))
        tab_to(page, doctor)
        page.keyboard.press('Enter')
        day = page.get_by_label('Date', exact=True)
        expect(page.locator('#book').get_by_role('button', name='Change', exact=True).last).to_be_focused()
    else:
        day = select_doctor(page)
        page.locator('#book').get_by_role('button', name='Change', exact=True).last.focus()
    page.keyboard.press('Tab')
    expect(day).to_be_focused()
    evidence(page, 'booking-keyboard-focus')
    day.fill(TOMORROW.isoformat())
    first = slot(page, '09:00 AM')
    expect(first).to_be_enabled()
    tab_to(page, first)
    page.keyboard.press('Space')
    notes = page.locator('#book textarea')
    tab_to(page, notes)
    page.keyboard.press('Tab')
    expect(confirm(page)).to_be_focused()
    evidence(page, 'booking-form')

    # Another synthetic patient takes the selected slot after it was displayed.
    appointment(patient=2, hour=time(9))
    db.session.commit()
    before = snapshots()
    with page.expect_response(lambda r: r.url.endswith('/api/patient/appointments') and
                              r.request.method == 'POST') as rejected:
        page.keyboard.press('Enter')
    assert rejected.value.status == 400
    error = page.locator('.patient-dashboard-wrapper .alert-danger')
    expect(error).to_contain_text(re.compile('slot is already booked', re.I))
    if os.environ.get('MEDIHUB_PHASE3_FIXED') == '1':
        expect(error).to_contain_text('Choose another available time')
    error.scroll_into_view_if_needed()
    evidence(page, 'booking-rejection')
    assert snapshots() == before

    day.focus()
    tab_to(page, slot(page, '10:00 AM'))
    page.keyboard.press('Space')
    tab_to(page, notes)
    page.keyboard.press('Tab')
    expect(confirm(page)).to_be_focused()
    with page.expect_response(lambda r: r.url.endswith('/api/patient/appointments') and
                              r.request.method == 'POST') as booked:
        page.keyboard.press('Enter')
    assert booked.value.status == 200
    expect(page.get_by_text('Appointment booked successfully!', exact=True)).to_be_visible()
    expect(confirm(page)).to_be_visible()
    evidence(page, 'booking-success')
    assert len(snapshots()) == 2
    assert snapshots()[-1][1:6] == (1, 1, TOMORROW.isoformat(), '10:00', 'booked')
