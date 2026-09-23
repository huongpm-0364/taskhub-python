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


def test_list_projects_filter_by_name(client):
    owner_id = _create_user(client)
    client.post("/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id})
    client.post("/api/projects/", json={"name": "Marketing Site", "owner_id": owner_id})

    response = client.get("/api/projects/", params={"name": "taskhub"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "TaskHub Core"


def test_list_projects_filter_by_owner(client):
    owner_id = _create_user(client)
    other_owner_id = client.post(
        "/api/users/",
        json={"email": "other@example.com", "username": "other", "password": "secret123"},
    ).json()["id"]
    client.post("/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id})
    client.post("/api/projects/", json={"name": "Other Project", "owner_id": other_owner_id})

    response = client.get("/api/projects/", params={"owner_id": owner_id})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["owner_id"] == owner_id


def test_delete_project_without_tasks(client):
    owner_id = _create_user(client)
    project = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id}
    ).json()

    response = client.delete(f"/api/projects/{project['id']}")
    assert response.status_code == 204

    response = client.get(f"/api/projects/{project['id']}")
    assert response.status_code == 404


def test_delete_project_with_tasks_is_rejected(client):
    owner_id = _create_user(client)
    project = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id}
    ).json()
    client.post("/api/tasks/", json={"title": "Setup env", "project_id": project["id"]})

    response = client.delete(f"/api/projects/{project['id']}")
    assert response.status_code == 409

    response = client.get(f"/api/projects/{project['id']}")
    assert response.status_code == 200
