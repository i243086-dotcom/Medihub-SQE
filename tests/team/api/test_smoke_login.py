def test_arjun_login_returns_token(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "arjun", "password": "arjun"},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["success"] is True
    assert body["data"]["user"]["username"] == "arjun"
    assert body["data"]["token"]


def test_wrong_password_rejected(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "arjun", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.get_json()["success"] is False
