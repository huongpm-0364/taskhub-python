def test_create_user(client):
    response = client.post(
        "/api/users/",
        json={"email": "alice@example.com", "username": "alice", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert "password" not in data
    assert "hashed_password" not in data


def test_get_user(client):
    created = client.post(
        "/api/users/",
        json={"email": "bob@example.com", "username": "bob", "password": "secret123"},
    ).json()

    response = client.get(f"/api/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == "bob"


def test_get_user_not_found(client):
    response = client.get("/api/users/999")
    assert response.status_code == 404


def test_list_users(client):
    client.post(
        "/api/users/",
        json={"email": "carol@example.com", "username": "carol", "password": "secret123"},
    )

    response = client.get("/api/users/")
    assert response.status_code == 200
    assert len(response.json()) == 1
