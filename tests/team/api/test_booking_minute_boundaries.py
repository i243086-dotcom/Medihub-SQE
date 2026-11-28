"""Fill the points adjacent to the existing exact-hour booking API cases."""

from datetime import time

import pytest

from phase2_support import TOMORROW, booking_payload, snapshots


@pytest.mark.parametrize(
    ("start", "expected_status"),
    [
        ("08:59", 400), ("09:01", 200),
        ("13:01", 400),
        ("14:59", 400), ("15:01", 200),
        ("18:59", 200), ("19:01", 400),
    ],
    ids=["0859", "0901", "1301", "1459", "1501", "1859", "1901"],
)
def test_booking_period_minute_edge(phase2, start, expected_status, record_property):
    client, tokens = phase2
    before = snapshots(include_seconds=True)
    response = client.post(
        "/api/patient/appointments", json=booking_payload(hour=start), headers=tokens["arjun"]
    )
    after = snapshots(include_seconds=True)
    record_property("input", start)
    record_property("expected_status", expected_status)
    record_property("actual_status", response.status_code)
    record_property("rows_before", repr(before))
    record_property("rows_after", repr(after))
    assert response.status_code == expected_status

    if expected_status == 400:
        assert "Invalid time slot" in response.json["message"]
        assert after == before
    else:
        key = response.json["data"]["appointment"]["id"]
        assert after == before + [
            (key, 1, 1, TOMORROW.isoformat(), time.fromisoformat(start).isoformat(), "booked", "")
        ]
