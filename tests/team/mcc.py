"""Enumerate the six BR-02 predicates in route evaluation order."""

from itertools import product

PREDICATES = (
    "patient_not_blacklisted", "doctor_active", "date_not_past",
    "period_available", "doctor_slot_free", "patient_time_free",
)
REJECTIONS = (
    (403, "blacklisted"), (404, "inactive"), (400, "past dates"),
    (400, "not available"), (400, "slot is already booked"), (400, "appointment at this time"),
)
ROWS = list(product((True, False), repeat=len(PREDICATES)))


def case_id(bits):
    return "MCC-" + "".join("1" if bit else "0" for bit in bits)


def oracle(bits):
    if all(bits):
        return 200, "booked successfully"
    return REJECTIONS[bits.index(False)]
