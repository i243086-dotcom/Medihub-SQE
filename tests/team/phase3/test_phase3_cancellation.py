"""Phase 3 real cancellation and persistence after reload."""

from playwright.sync_api import expect

from database import db
from phase2_support import appointment, snapshots
from e2e.test_appointment_flows import assets, browser_app, login, patient_list
from test_phase3_booking import evidence


def test_phase3_cancel_active_appointment_and_reload(browser_app, page):
    appointment()
    db.session.commit()
    before = snapshots()[0]
    login(page, browser_app)
    row = patient_list(page).filter(has_text='Ajay Kumar')
    expect(row.get_by_text('Booked', exact=True)).to_be_visible()
    evidence(page, 'cancellation-active')
    cancel = row.get_by_title('Cancel Appointment')
    cancel.focus()
    expect(cancel).to_be_focused()
    page.keyboard.press('Enter')
    dialog = page.locator('#cancelAppointmentModal')
    expect(dialog).to_be_visible()
    dialog.get_by_role('button', name='Yes, Cancel Appointment').click()
    expect(page.get_by_text('Appointment cancelled successfully', exact=True)).to_be_visible()
    expect(row.get_by_text('Cancelled', exact=True)).to_be_visible()
    evidence(page, 'cancellation-success')
    assert snapshots() == [(*before[:5], 'cancelled', before[6])]
    page.reload()
    expect(page.get_by_role('button', name='Logout')).to_be_visible()
    expect(patient_list(page).filter(has_text='Ajay Kumar').get_by_text('Cancelled', exact=True)).to_be_visible()
