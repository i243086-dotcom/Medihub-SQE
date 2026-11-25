import smtplib


def test_cancel_never_opens_smtp_connection(client, monkeypatch):
    calls = []

    class Boom(smtplib.SMTP):
        def __init__(self, *a, **k):
            calls.append(a)
            raise AssertionError("SMTP connection attempted during tests")

    monkeypatch.setattr(smtplib, "SMTP", Boom)
    login = client.post("/api/auth/login", json={"username": "arjun", "password": "arjun"})
    h = {"Authorization": "Bearer " + login.get_json()["data"]["token"]}
    from test_smoke_high_risk import apt_date, first_doctor_id, book
    r = book(client, h, first_doctor_id(), apt_date(), "10:00")
    apt_id = r.get_json()["data"]["appointment"]["id"]
    assert client.delete("/api/patient/appointments/%d" % apt_id, headers=h).status_code == 200
    assert calls == []
