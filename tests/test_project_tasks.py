from sqlalchemy import event


def _create_user(client) -> int:
    return client.post(
        "/api/users/",
        json={"email": "pm@example.com", "username": "pm", "password": "secret123"},
    ).json()["id"]


def _create_project(client) -> int:
    owner_id = _create_user(client)
    return client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id}
    ).json()["id"]


def _count_queries(engine, fn):
    queries = []

    def counter(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(engine, "before_cursor_execute", counter)
    try:
        fn()
    finally:
        event.remove(engine, "before_cursor_execute", counter)
    return len(queries)


def test_get_project_includes_nested_tasks(client):
    project_id = _create_project(client)
    client.post("/api/tasks/", json={"title": "Setup env", "project_id": project_id})

    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Setup env"


def test_list_project_tasks(client):
    project_id = _create_project(client)
    client.post("/api/tasks/", json={"title": "Setup env", "project_id": project_id})

    response = client.get(f"/api/projects/{project_id}/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Setup env"
    assert data[0]["tags"] == []


def test_list_project_tasks_project_not_found(client):
    response = client.get("/api/projects/999/tasks")
    assert response.status_code == 404


def test_create_task_in_project(client):
    project_id = _create_project(client)

    response = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Write tests"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write tests"
    assert data["project_id"] == project_id


def test_create_task_in_project_not_found(client):
    response = client.post("/api/projects/999/tasks", json={"title": "Write tests"})
    assert response.status_code == 404


def test_list_project_tasks_query_count_does_not_scale_with_task_count(client, db_session):
    project_id = _create_project(client)
    engine = db_session.get_bind()

    for i in range(2):
        client.post("/api/tasks/", json={"title": f"Task {i}", "project_id": project_id})
    query_count_with_2_tasks = _count_queries(
        engine, lambda: client.get(f"/api/projects/{project_id}/tasks")
    )

    for i in range(2, 6):
        client.post("/api/tasks/", json={"title": f"Task {i}", "project_id": project_id})
    query_count_with_6_tasks = _count_queries(
        engine, lambda: client.get(f"/api/projects/{project_id}/tasks")
    )

    assert query_count_with_2_tasks == query_count_with_6_tasks
