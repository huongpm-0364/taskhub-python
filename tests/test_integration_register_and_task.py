"""Integration test for the register -> create task flow (bài 7).

Unlike the other test files (one behavior per test function), this one walks through
the whole journey a real client would take end-to-end, using TestClient exactly as the
FastAPI testing docs recommend: register an account, log in with it, then use that
account to create a project and a task.
"""


def test_register_then_create_task_flow(client):
    # 1. Register a new account.
    register_response = client.post(
        "/api/users/register",
        json={
            "email": "integration@example.com",
            "username": "integration",
            "password": "secret123",
        },
    )
    assert register_response.status_code == 201
    user = register_response.json()
    assert user["username"] == "integration"
    assert "password" not in user
    assert "hashed_password" not in user

    # 2. Log in with the freshly registered account.
    login_response = client.post(
        "/api/users/login",
        data={"username": "integration", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. The token really identifies this account.
    me_response = client.get("/api/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["id"] == user["id"]

    # 4. Create a project owned by that user.
    project_response = client.post(
        "/api/projects/", json={"name": "Integration Project", "owner_id": user["id"]}
    )
    assert project_response.status_code == 201
    project = project_response.json()

    # 5. Create a task under that project.
    task_response = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Write integration test"},
    )
    assert task_response.status_code == 201
    task = task_response.json()
    assert task["project_id"] == project["id"]
    assert task["status"] == "todo"

    # 6. The task shows up when listing tasks for the project...
    list_response = client.get(f"/api/projects/{project['id']}/tasks")
    assert list_response.status_code == 200
    assert [t["id"] for t in list_response.json()] == [task["id"]]

    # 7. ...and nested under the project detail too.
    project_detail = client.get(f"/api/projects/{project['id']}")
    assert len(project_detail.json()["tasks"]) == 1
    assert project_detail.json()["tasks"][0]["id"] == task["id"]
