from datetime import timedelta

from app.core.security import create_access_token


def _register(client, username="alice", email="alice@example.com", password="secret123"):
    return client.post(
        "/api/users/register",
        json={"email": email, "username": username, "password": password},
    )


def test_register(client):
    response = _register(client)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username_is_rejected(client):
    _register(client)
    response = _register(client, email="someone-else@example.com")
    assert response.status_code == 409


def test_login_success(client):
    _register(client)

    response = client.post(
        "/api/users/login",
        data={"username": "alice", "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_wrong_password(client):
    _register(client)

    response = client.post(
        "/api/users/login",
        data={"username": "alice", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        "/api/users/login",
        data={"username": "ghost", "password": "secret123"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_me_returns_current_user(client):
    _register(client)
    token = client.post(
        "/api/users/login", data={"username": "alice", "password": "secret123"}
    ).json()["access_token"]

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_me_route_is_not_shadowed_by_user_id_route(client):
    # Regression guard: "/me" must be registered before "/{user_id}", otherwise this
    # request would incorrectly match "/{user_id}" and fail int conversion of "me".
    response = client.get("/api/users/me")
    assert response.status_code == 401  # not 422


def test_update_me(client):
    _register(client)
    token = client.post(
        "/api/users/login", data={"username": "alice", "password": "secret123"}
    ).json()["access_token"]

    response = client.put(
        "/api/users/me",
        json={"username": "alice2"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "alice2"

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.json()["username"] == "alice2"


def test_update_me_duplicate_username_is_rejected(client):
    _register(client, username="alice", email="alice@example.com")
    _register(client, username="bob", email="bob@example.com")
    token = client.post(
        "/api/users/login", data={"username": "bob", "password": "secret123"}
    ).json()["access_token"]

    response = client.put(
        "/api/users/me",
        json={"username": "alice"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


def test_me_rejects_expired_token(client):
    _register(client)
    expired_token = create_access_token("alice", expires_delta=timedelta(minutes=-1))

    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401


def test_me_rejects_garbage_token(client):
    response = client.get(
        "/api/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
