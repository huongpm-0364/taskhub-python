def _create_project(client) -> int:
    user = client.post(
        "/api/users/",
        json={"email": "pm@example.com", "username": "pm", "password": "secret123"},
    ).json()
    project = client.post(
        "/api/projects/",
        json={"name": "TaskHub Core", "owner_id": user["id"]},
    ).json()
    return project["id"]


def test_create_task(client):
    project_id = _create_project(client)

    response = client.post(
        "/api/tasks/",
        json={"title": "Setup env", "project_id": project_id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Setup env"
    assert data["status"] == "todo"
    assert data["project_id"] == project_id


def test_get_task_not_found(client):
    response = client.get("/api/tasks/999")
    assert response.status_code == 404


def test_list_tasks(client):
    project_id = _create_project(client)
    client.post("/api/tasks/", json={"title": "Setup env", "project_id": project_id})

    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 1
