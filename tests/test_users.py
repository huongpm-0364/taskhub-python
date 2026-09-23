from app.models.enums import UserRole
from app.models.user import User


def _login(client, username, password="secret123") -> str:
    return client.post(
        "/api/users/login", data={"username": username, "password": password}
    ).json()["access_token"]


def _make_admin(db_session, username) -> None:
    user = db_session.query(User).filter(User.username == username).first()
    user.role = UserRole.admin
    db_session.commit()


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


def test_list_users_requires_auth(client):
    response = client.get("/api/users/")
    assert response.status_code == 401


def test_list_users_requires_admin(client):
    client.post(
        "/api/users/",
        json={"email": "carol@example.com", "username": "carol", "password": "secret123"},
    )
    token = _login(client, "carol")

    response = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_list_users_as_admin(client, db_session):
    client.post(
        "/api/users/",
        json={"email": "carol@example.com", "username": "carol", "password": "secret123"},
    )
    client.post(
        "/api/users/",
        json={"email": "root@example.com", "username": "root", "password": "secret123"},
    )
    _make_admin(db_session, "root")
    token = _login(client, "root")

    response = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_profile(client):
    user = client.post(
        "/api/users/",
        json={"email": "dave@example.com", "username": "dave", "password": "secret123"},
    ).json()
    project = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": user["id"]}
    ).json()
    client.post(
        "/api/tasks/",
        json={"title": "Setup env", "project_id": project["id"], "assignee_id": user["id"]},
    )

    response = client.get(f"/api/users/{user['username']}/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "dave"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["name"] == "TaskHub Core"
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Setup env"


def test_get_user_profile_not_found(client):
    response = client.get("/api/users/ghost/profile")
    assert response.status_code == 404
