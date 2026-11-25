"""Phase 1 acceptance cases plus separately identified policy observations."""

from datetime import datetime, timedelta, timezone


P = "/api/patient"
D = "/api/doctor"
A = "/api/admin"
TODAY = "2026-11-23"
TOMORROW = "2026-11-24"
YESTERDAY = "2026-11-22"
HOURS = [f"{hour:02}:00" for hour in (9, 10, 11, 12, 15, 16, 17, 18)]
STATES = ("booked", "cancelled", "completed")


def api_cases(a):
    def get(path, key, actor="arjun", **query):
        status, payload = a.request("GET", path, actor, params=query)
        assert status == 200, (status, payload)
        return payload["data"][key]

    def slots(day=TOMORROW, doctor=1, actor="arjun"):
        return get(P + "/available-slots", "slots", actor, doctor_id=doctor, date=day)

    def slot_times(day=TOMORROW):
        return [slot["appointment_time"] for slot in slots(day)]

    def booking(doctor=1, day=TOMORROW, time="10:00", actor="arjun", code=200,
                message=None, omit=None, notes=None):
        body = {"doctor_id": doctor, "appointment_date": day, "appointment_time": time}
        if notes is not None:
            body["notes"] = notes
        if omit:
            del body[omit]
        before = a.rows()
        status, response = a.request("POST", P + "/appointments", actor, json=body)
        after = a.rows()
        if code != 200:
            assert after == before, after
        assert status == code, (status, response.get("message"), after)
        if message:
            assert message in response.get("message", ""), response.get("message")
        if code != 200:
            return None
        patient_id = 1 if actor == "arjun" else 2
        appointment = response["data"]["appointment"]
        assert len(after) == len(before) + 1, after
        assert after[-1][:6] == (appointment["id"], patient_id, doctor, day, time[:5] + ":00.000000",
                                 "booked"), after
        return appointment["id"]

    def cancellation(appointment, actor="arjun", code=200):
        before = a.rows()
        status, response = a.request("DELETE", f"{P}/appointments/{appointment}", actor)
        after = a.rows()
        assert status == code, (status, response.get("message"), after)
        if code == 200:
            assert len(after) == len(before) == 1 and after[0][:5] == before[0][:5], after
            assert after[0][5] == "cancelled" and after[0][6] != before[0][6], after
        else:
            assert after == before, after

    def change_status(role, actor, appointment, target, code=200):
        path = f"{D}/appointments/{appointment}/status" if role == "doctor" else f"{A}/appointments/{appointment}"
        before = a.rows()
        status, response = a.request("PUT", path, actor, json={"status": target})
        after = a.rows()
        if code != 200:
            assert after == before, after
        assert status == code, (status, response.get("message"), after)
        if code == 200:
            assert len(after) == 1 and after[0][5] == target, after

    def available(day):
        a.db_sql("INSERT INTO doctor_availability (doctor_id, availability_date, slot_type, is_available) "
                 "VALUES (1, ?, 'morning', 1)", (day,))
        a.steps.append({"fixture_available": day})

    def discovery():
        a.db_sql("UPDATE doctors SET is_active = 0 WHERE id = 2")
        doctors = get(P + "/doctors", "doctors")
        departments = get(P + "/departments", "departments")
        assert [x["name"] for x in doctors] == ["Ajay Kumar"]
        assert [(x["name"], x["doctor_count"]) for x in departments] == [("Cardiology", 1)]
        assert [x["id"] for x in get(P + "/doctors", "doctors", department="Cardiology")] == [1]
        assert get(P + "/doctors", "doctors", department="Neurology") == []
        assert get(P + "/departments", "departments", "admin") == departments
        assert a.request("GET", P + "/doctors", "admin")[0] == 403

    def slot_labels():
        booking()
        result = slots()
        assert [x["appointment_time"] for x in result] == HOURS
        assert [x["status"] for x in result] == ["available", "booked"] + ["available"] * 6
        assert result[0]["display"] == "09:00 AM - 10:00 AM"
        assert result[-1]["display"] == "06:00 PM - 07:00 PM"
        assert result == slots(actor="admin")
        assert a.request("GET", P + "/available-slots", "ajay",
                         params={"doctor_id": 1, "date": TOMORROW})[0] == 403

    def cancel_readback():
        apt = booking()
        cancellation(apt)
        for prefix, actor in ((P, "arjun"), (D, "ajay")):
            rows = get(prefix + "/appointments", "appointments", actor)
            assert [(x["id"], x["status"]) for x in rows] == [(apt, "cancelled")]
        assert get(P + "/appointments", "appointments", "vikram") == []
        assert get(D + "/appointments", "appointments", "rajesh") == []
        assert get(D + "/appointments", "appointments", "ajay", time_filter="upcoming") == []
        assert next(x for x in slots() if x["appointment_time"] == "10:00")["status"] == "available"

    def rebook():
        apt = booking()
        cancellation(apt)
        assert next(x for x in slots() if x["appointment_time"] == "10:00")["status"] == "available"
        booking(actor="vikram")

    def inactive():
        a.db_sql("UPDATE doctors SET is_active = 0 WHERE id = 1")
        booking(code=404, message="inactive")

    def blacklist():
        status, _ = a.request("PUT", A + "/patients/1/blacklist", "admin")
        assert status == 200
        assert a.db_sql("SELECT is_blacklisted FROM patients WHERE id=1") == [(1,)]
        booking(code=403, message="blacklisted")

    def unavailable():
        a.db_sql("UPDATE doctor_availability SET is_available = 0 WHERE doctor_id = 1 "
                 "AND availability_date = ? AND slot_type = 'morning'", (TOMORROW,))
        assert slot_times() == HOURS[4:]
        booking(code=400, message="not available")

    def day_case(day, code, has_slots):
        if day == YESTERDAY or day > "2026-11-30":
            available(day)
        assert bool(slots(day)) is has_slots
        booking(day=day, code=code)

    def raw_booking(code, **kwargs):
        before = a.rows()
        actual, response = a.request("POST", P + "/appointments", **kwargs)
        assert a.rows() == before, a.rows()
        assert actual == code, (actual, response)

    def same_day(utc, visible):
        a.set_clock(utc)
        assert ("09:00" in slot_times(TODAY)) is visible
        booking(day=TODAY, time="09:00", code=200 if visible else 400)

    def timezone_midnight():
        a.set_clock("18:45:00")
        utc = a.steps[-1]["clock_utc"]
        instant = datetime.fromisoformat(utc.replace("Z", "+00:00"))
        ist = instant.astimezone(timezone(timedelta(hours=5, minutes=30)))
        pkt = instant.astimezone(timezone(timedelta(hours=5)))
        assert (ist.date().isoformat(), pkt.date().isoformat()) == (TOMORROW, TODAY)
        a.steps.append({"ist": ist.isoformat(), "pkt": pkt.isoformat()})
        booking(day=TODAY, code=400, message="past dates")
        assert slot_times() == HOURS

    def previous_state(source):
        apt = booking()
        if source != "booked":
            a.db_sql("UPDATE appointments SET status = ? WHERE id = ?", (source, apt))
            a.steps.append({"fixture_status": source, "rows": a.rows()})
        return apt

    def started_booking_cancellation():
        apt = booking(day=TODAY, time="09:00")
        a.set_clock("04:30:00")
        cancellation(apt)

    a.case("P1-A01", "FR-01;BR-04", "Active doctor/specialization discovery and source-defined read roles", discovery)
    a.case("P1-A02", "FR-02;BR-01;BR-04", "Eight hourly labels, exact booked flag and slot read roles", slot_labels)
    a.case("P1-A03", "FR-03;BR-02", "All six eligibility conditions true creates one booked row", booking)
    a.case("P1-A04", "FR-03;FR-06;FR-02;BR-02;H-01", "A-01: a different patient can rebook the released slot", rebook)
    for number, key in enumerate(("doctor_id", "appointment_date", "appointment_time"), 1):
        a.case(f"P1-V0{number}", "FR-04", f"Missing {key} gives 400 and does not write",
               lambda: booking(omit=key, code=400))
    a.case("P1-V04", "FR-04", "Unknown doctor gives 404", lambda: booking(doctor=900, code=404))
    a.case("P1-V05", "FR-04;BR-02", "Inactive doctor gives 404 even with otherwise available slot", inactive)
    a.case("P1-V06", "FR-04", "Impossible date gives a client error", lambda: booking(day="2026-02-30", code=400))
    for number, body in enumerate(({"appointment_date": 20261124}, {"appointment_time": "abc"},
                                   {"appointment_time": 900}, {"doctor_id": []},
                                   {"appointment_time": "24:00"}), 7):
        payload = {"doctor_id": 1, "appointment_date": TOMORROW, "appointment_time": "10:00", **body}
        a.case(f"P1-V{number:02}", "FR-04;BR-01;H-03", f"Invalid field {body} gives 400 and does not write",
               lambda: raw_booking(400, json=payload))
    for suffix, data, code in (("12", "null", 400), ("13", "", 400), ("14", "[1]", 400)):
        a.case("P1-V" + suffix, "FR-04;H-03", f"Invalid JSON document {data!r} gives 400 without writing",
               lambda: raw_booking(code, data=data, headers={"Content-Type": "application/json"}))
    a.case("P1-A05", "FR-05;BR-02", "Duplicate retry leaves one row",
           lambda: (booking(), booking(code=400, message="already booked")))
    a.case("P1-A06", "FR-05;BR-02", "Other patient cannot book the occupied doctor slot",
           lambda: (booking(), booking(actor="vikram", code=400, message="already booked")))
    a.case("P1-A07", "FR-05;BR-02", "Same patient cannot book a second doctor at the same date/time",
           lambda: (booking(), booking(doctor=2, code=400, message="already have")))
    a.case("P1-A08", "FR-06;FR-08;BR-03;BR-04", "Owner cancels, status visible to the patient and assigned doctor",
           cancel_readback)
    a.case("P1-A09", "FR-06;BR-03", "A-02: owning patient can cancel a booked slot after its start",
           started_booking_cancellation)
    a.case("P1-A10", "FR-07;BR-03;BR-04", "Other patient cannot cancel or change the row",
           lambda: cancellation(booking(), "vikram", 404))
    a.case("P1-A11", "FR-07;BR-03", "Absent appointment returns 404 and does not write",
           lambda: cancellation(700, code=404))
    for number, source in enumerate(("cancelled", "completed", "available"), 12):
        a.case(f"P1-A{number}", "FR-07;BR-03", f"Patient cancellation from {source} returns 400",
               lambda: cancellation(previous_state(source), code=400))
    a.case("P1-A15", "FR-07;BR-03", "Repeat cancellation returns 400",
           lambda: (apt := booking(), cancellation(apt), cancellation(apt, code=400)))
    for actor, code in (("ajay", 403), ("admin", 403), (None, 401)):
        for action in ("book", "cancel"):
            a.case(f"P1-ROLE-{actor or 'anonymous'}-{action}", "FR-09;BR-04", f"{actor} gets {code} for {action}",
                   lambda: (booking(actor=actor, code=code) if action == "book"
                            else cancellation(booking(), actor, code)))
    a.case("P1-A16", "FR-10;BR-02", "Blacklisted patient denied even with all other eligibility conditions true",
           blacklist)
    a.case("P1-A17", "FR-02;FR-03;BR-02", "Availability false hides morning slots and rejects booking", unavailable)
    for suffix, day, code, has_slots in (
        ("01", YESTERDAY, 400, True), ("02", TODAY, 200, True), ("03", TOMORROW, 200, True),
        ("04", "2026-11-28", 200, True), ("05", "2026-11-29", 200, True),
        ("06", "2026-11-30", 400, False), ("07", "2026-12-20", 200, True),
    ):
        a.case("P1-D" + suffix, "FR-02;FR-03;FR-04;BR-01;BR-02" + (";H-04" if day == YESTERDAY else ""),
               f"{day}: booking {code}, slot listing present={has_slots}",
               lambda: day_case(day, code, has_slots))
    for clock, visible in (("03:29:59", True), ("03:30:00", False), ("03:30:01", False), ("04:00:00", False)):
        a.case("P1-C-" + clock.replace(":", ""), "FR-02;FR-03;BR-01",
               f"09:00 same-day slot under IST at UTC {clock}: visible={visible}",
               lambda: same_day(clock, visible))
    a.case("P1-C-midnight", "FR-02;FR-04;BR-01", "Clock identifies next day in IST, same day in PKT",
           timezone_midnight)
    for hour in (8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20):
        slot = f"{hour:02}:00"
        accepted = slot in HOURS

        def boundary_case():
            assert (slot in slot_times()) is accepted
            booking(time=slot, code=200 if accepted else 400)

        a.case(f"P1-B-{hour:02}", "FR-02;FR-03;BR-01",
               f"{slot} is {'inside' if accepted else 'outside'} the hourly start list and API hour band",
               boundary_case)
    for slot in ("09:30", "12:59"):
        def minute_case():
            assert slot not in slot_times()
            booking(time=slot, code=400)

        a.case("P1-B-" + slot.replace(":", ""), "FR-02;FR-03;BR-01",
               f"Hourly booking contract rejects {slot} and UI omits it",
               minute_case)
    for role, actor in (("doctor", "ajay"), ("admin", "admin")):
        for source in STATES:
            for target in STATES:
                policy = (role == "doctor" and source != "booked") or role == "admin"
                a.case(f"P1-{role}-{source}-{target}", f"Proposed FR-{'11' if role == 'doctor' else '12'};BR-04;H-02",
                       f"Characterize {role} {source} to {target}", lambda: change_status(
                           role, actor, previous_state(source), target), policy=policy)
            a.case(f"P1-{role}-{source}-invalid", f"Proposed FR-{'11' if role == 'doctor' else '12'};H-02",
                   f"Unknown status rejected from {source} with no write",
                   lambda: change_status(role, actor, previous_state(source), "banana", 400))
    for actor, code in (("rajesh", 404), ("arjun", 403), ("admin", 403), (None, 401)):
        a.case(f"P1-doctor-denial-{actor or 'anonymous'}", "Proposed FR-11;BR-04", "Doctor assignment and role enforced",
               lambda: change_status("doctor", actor, booking(), "cancelled", code))
    for actor, code in (("ajay", 403), ("arjun", 403), (None, 401)):
        a.case(f"P1-admin-denial-{actor or 'anonymous'}", "Proposed FR-12;BR-04", "Admin role enforced",
               lambda: change_status("admin", actor, booking(), "cancelled", code))


def browser_cases(a, assets):
    from playwright.sync_api import expect, sync_playwright

    sources = {
        "https://unpkg.com/vue@3/dist/vue.global.js": ("vue.global.js", "application/javascript"),
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js":
            ("bootstrap.bundle.min.js", "application/javascript"),
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css":
            ("bootstrap.min.css", "text/css"),
    }
    if not assets or not all((assets / name).is_file() for name, _ in sources.values()):
        raise RuntimeError("Offline Vue and Bootstrap assets are required via --assets")

    def network(route):
        url = route.request.url
        if url.startswith(a.url + "/"):
            route.continue_()
        elif url in sources:
            filename, mime = sources[url]
            route.fulfill(path=assets / filename, content_type=mime)
        else:
            route.abort()

    with sync_playwright() as playwright, playwright.chromium.launch() as browser:
        def check_ui():
            with browser.new_context(timezone_id="Asia/Karachi", viewport={"width": 1280, "height": 900}) as ctx:
                ctx.route("**/*", network)
                page = ctx.new_page()
                page.set_default_timeout(8000)
                page.clock.set_fixed_time(datetime.fromisoformat(TODAY + "T02:30:00+00:00"))
                a.steps.append({"chromium": browser.version, "timezone": "Asia/Karachi"})

                def login(username, password):
                    page.get_by_role("button", name="Sign In", exact=True).first.click()
                    page.get_by_placeholder("Enter your username").fill(username)
                    page.locator("input[type=password]").fill(password)
                    page.locator("form button[type=submit]").click()
                    expect(page.get_by_role("button", name="Logout")).to_be_visible()

                page.goto(a.url, wait_until="domcontentloaded")
                login("arjun", "arjun")
                page.get_by_role("tab", name="Book Appointment").click()
                expect(page.get_by_text("Choose a specialization to get started")).to_be_visible()
                expect(page.get_by_text("Neurology", exact=True)).to_be_visible()
                page.get_by_text("Cardiology", exact=True).click()
                expect(page.get_by_text("Select a doctor from the list")).to_be_visible()
                page.get_by_text("Dr. Ajay Kumar", exact=True).click()
                date_input = page.locator("#book input[type=date]")
                expect(date_input).to_have_attribute("min", TODAY)
                expect(page.get_by_role("button", name="Confirm Booking")).to_be_disabled()
                date_input.fill(TOMORROW)
                slot = page.get_by_role("button", name="09:00 AM - 10:00 AM Morning")
                expect(slot).to_be_enabled()
                expect(page.get_by_role("button", name="06:00 PM - 07:00 PM Evening")).to_be_visible()
                a.steps.append({"ui": "Specialization, doctor, UTC date minimum, disabled submit before slot and slot controls"})
                slot.click()
                with page.expect_response(lambda res: res.url.endswith(P + "/appointments") and
                                          res.request.method == "POST") as booked:
                    page.get_by_role("button", name="Confirm Booking").click()
                assert booked.value.status == 200
                expect(page.get_by_text("Appointment booked successfully", exact=False).first).to_be_visible()
                assert len(a.rows()) == 1 and a.rows()[0][3:6] == (TOMORROW, "09:00:00.000000", "booked")
                a.steps.append({"ui": "Appointment booked successfully", "db_after": a.rows()})
                page.screenshot(path=a.output / (a.output_revision + "-booking.png"))

                page.get_by_role("tab", name="My Appointments").click()
                row = page.get_by_role("row").filter(has_text="Ajay Kumar")
                expect(row.get_by_text("Booked", exact=True)).to_be_visible()
                row.get_by_title("Cancel Appointment").click()
                page.get_by_role("button", name="No, Keep it").click()
                expect(row.get_by_text("Booked", exact=True)).to_be_visible()
                assert a.rows()[0][5] == "booked"
                row.get_by_title("Cancel Appointment").click()
                with page.expect_response(lambda res: res.request.method == "DELETE" and
                                          P + "/appointments/" in res.url) as cancelled:
                    page.get_by_role("button", name="Yes, Cancel Appointment").click()
                assert cancelled.value.status == 200
                expect(page.get_by_text("Appointment cancelled successfully", exact=True)).to_be_visible()
                expect(row.get_by_text("Cancelled", exact=True)).to_be_visible()
                expect(row.get_by_title("Cancel Appointment")).to_have_count(0)
                assert len(a.rows()) == 1 and a.rows()[0][5] == "cancelled"
                a.steps.append({"ui": "No, Keep it retained Booked. Yes, Cancel Appointment changed it to Cancelled.",
                                "db_after": a.rows()})
                page.screenshot(path=a.output / (a.output_revision + "-cancellation.png"))

                page.get_by_role("button", name="Logout").click()
                expect(page.get_by_role("button", name="Sign In", exact=True).first).to_be_visible()
                page.reload(wait_until="domcontentloaded")
                login("ajay", "ajay.kumar123")
                page.get_by_role("tab", name="Appointments").click()
                expect(page.get_by_role("tab", name="Book Appointment")).to_have_count(0)
                doctor_row = page.get_by_role("row").filter(has_text="Arjun Patel")
                expect(doctor_row.get_by_text("Cancelled", exact=True)).to_be_visible()
                a.steps.append({"ui": "Assigned doctor's appointment shows Cancelled"})
                page.screenshot(path=a.output / (a.output_revision + "-doctor.png"))

        a.case("P1-UI01", "FR-01;FR-02;FR-03;FR-06;FR-08;BR-01;BR-03",
               "Patient browser booking, keep/cancel, persisted status and doctor view", check_ui)
