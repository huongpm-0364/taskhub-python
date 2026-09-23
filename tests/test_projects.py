def _create_user(client) -> int:
    response = client.post(
        "/api/users/",
        json={"email": "owner@example.com", "username": "owner", "password": "secret123"},
    )
    return response.json()["id"]


def test_create_project(client):
    owner_id = _create_user(client)

    response = client.post(
        "/api/projects/",
        json={"name": "TaskHub Core", "owner_id": owner_id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TaskHub Core"
    assert data["owner_id"] == owner_id


def test_get_project_not_found(client):
    response = client.get("/api/projects/999")
    assert response.status_code == 404


def test_list_projects(client):
    owner_id = _create_user(client)
    client.post("/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id})

    response = client.get("/api/projects/")
    assert response.status_code == 200
    assert len(response.json()) == 1
