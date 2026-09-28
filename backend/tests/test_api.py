def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_register_login_me(client):
    body = {"email": "a@example.com", "name": "A", "password": "password123", "role": "educator"}
    assert client.post("/api/auth/register", json=body).status_code == 201
    assert client.post("/api/auth/register", json=body).status_code == 409
    login = client.post("/api/auth/login", json={"email": "a@example.com", "password": "password123"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/auth/me", headers=headers).json()["role"] == "educator"


def test_login_rejects_bad_password(client):
    body = {"email": "b@example.com", "name": "B", "password": "password123"}
    client.post("/api/auth/register", json=body)
    response = client.post("/api/auth/login", json={"email": "b@example.com", "password": "wrong-password"})
    assert response.status_code == 401


def test_simulations_require_auth(client):
    assert client.get("/api/simulations").status_code == 401


def test_list_and_read_simulation(client, auth_headers):
    listing = client.get("/api/simulations", headers=auth_headers).json()
    assert any(s["id"] == "cpr-adult" for s in listing)
    detail = client.get("/api/simulations/cpr-adult", headers=auth_headers).json()
    assert "action" not in detail["steps"][0]
    assert len(detail["actions"]) > len(detail["steps"])


def test_attempt_flow(client, auth_headers):
    perfect = [
        "check_scene_safety",
        "check_responsiveness",
        "call_emergency",
        "check_breathing",
        "start_compressions",
        "give_rescue_breaths",
        "use_aed",
    ]
    response = client.post(
        "/api/attempts",
        headers=auth_headers,
        json={"simulation_id": "cpr-adult", "actions": perfect, "duration_seconds": 40},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["score"] == data["max_score"]
    assert data["errors"] == []

    bad = client.post(
        "/api/attempts",
        headers=auth_headers,
        json={"simulation_id": "cpr-adult", "actions": ["give_water", "start_compressions"]},
    ).json()
    assert bad["score"] < bad["max_score"]
    assert bad["errors"]

    history = client.get("/api/attempts", headers=auth_headers).json()
    assert len(history) == 2


def test_unknown_simulation(client, auth_headers):
    response = client.post(
        "/api/attempts", headers=auth_headers, json={"simulation_id": "nope", "actions": []}
    )
    assert response.status_code == 404
