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


def test_create_task_default_priority(client):
    project_id = _create_project(client)

    response = client.post("/api/tasks/", json={"title": "Setup env", "project_id": project_id})
    assert response.json()["priority"] == "medium"


def test_list_tasks_filter_by_status(client):
    project_id = _create_project(client)
    client.post(
        "/api/tasks/",
        json={"title": "Todo task", "project_id": project_id, "status": "todo"},
    )
    client.post(
        "/api/tasks/",
        json={"title": "Done task", "project_id": project_id, "status": "done"},
    )

    response = client.get("/api/tasks/", params={"status": "done"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Done task"


def test_list_tasks_filter_by_priority(client):
    project_id = _create_project(client)
    client.post(
        "/api/tasks/",
        json={"title": "Low priority", "project_id": project_id, "priority": "low"},
    )
    client.post(
        "/api/tasks/",
        json={"title": "High priority", "project_id": project_id, "priority": "high"},
    )

    response = client.get("/api/tasks/", params={"priority": "high"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High priority"


def test_list_tasks_filter_by_status_and_priority_combined(client):
    project_id = _create_project(client)
    client.post(
        "/api/tasks/",
        json={
            "title": "Match",
            "project_id": project_id,
            "status": "todo",
            "priority": "high",
        },
    )
    client.post(
        "/api/tasks/",
        json={
            "title": "Wrong priority",
            "project_id": project_id,
            "status": "todo",
            "priority": "low",
        },
    )

    response = client.get("/api/tasks/", params={"status": "todo", "priority": "high"})
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Match"


def _login(client, username, password="secret123") -> str:
    return client.post(
        "/api/users/login", data={"username": username, "password": password}
    ).json()["access_token"]


def test_bookmark_task_requires_auth(client):
    project_id = _create_project(client)
    task = client.post(
        "/api/tasks/", json={"title": "Setup env", "project_id": project_id}
    ).json()

    response = client.post(f"/api/tasks/{task['id']}/bookmark")
    assert response.status_code == 401


def test_bookmark_task(client):
    project_id = _create_project(client)
    task = client.post(
        "/api/tasks/", json={"title": "Setup env", "project_id": project_id}
    ).json()
    token = _login(client, "pm")

    response = client.post(
        f"/api/tasks/{task['id']}/bookmark", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["task_id"] == task["id"]


def test_bookmark_task_twice_is_rejected(client):
    project_id = _create_project(client)
    task = client.post(
        "/api/tasks/", json={"title": "Setup env", "project_id": project_id}
    ).json()
    token = _login(client, "pm")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(f"/api/tasks/{task['id']}/bookmark", headers=headers)
    response = client.post(f"/api/tasks/{task['id']}/bookmark", headers=headers)
    assert response.status_code == 409


def test_bookmark_task_not_found(client):
    client.post(
        "/api/users/",
        json={"email": "someone@example.com", "username": "someone", "password": "secret123"},
    )
    token = _login(client, "someone")

    response = client.post(
        "/api/tasks/999/bookmark", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
