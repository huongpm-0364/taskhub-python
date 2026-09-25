from app.core import email


def _create_user(client, username, email_addr) -> dict:
    return client.post(
        "/api/users/",
        json={"email": email_addr, "username": username, "password": "secret123"},
    ).json()


def _login(client, username, password="secret123") -> str:
    return client.post(
        "/api/users/login", data={"username": username, "password": password}
    ).json()["access_token"]


def _auth_headers(client, username) -> dict:
    return {"Authorization": f"Bearer {_login(client, username)}"}


def test_comment_notifies_the_assignee(client, monkeypatch):
    sent = []
    monkeypatch.setattr(email, "send_email", lambda **kwargs: sent.append(kwargs))

    owner = _create_user(client, "owner", "owner@example.com")
    dev = _create_user(client, "dev", "dev@example.com")
    project = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner["id"]}
    ).json()
    task = client.post(
        "/api/tasks/", json={"title": "Setup env", "project_id": project["id"]}
    ).json()
    client.post(
        f"/api/tasks/{task['id']}/assign",
        json={"assignee_id": dev["id"]},
        headers=_auth_headers(client, "owner"),
    )
    sent.clear()  # assign_task itself only writes a comment row, doesn't post via the API

    response = client.post(
        f"/api/tasks/{task['id']}/comments",
        json={"content": "How's it going?"},
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 201
    assert len(sent) == 1
    assert sent[0]["to"] == "dev@example.com"
    assert str(task["id"]) in sent[0]["subject"]


def test_commenting_on_own_task_does_not_notify_yourself(client, monkeypatch):
    sent = []
    monkeypatch.setattr(email, "send_email", lambda **kwargs: sent.append(kwargs))

    owner = _create_user(client, "owner", "owner@example.com")
    project = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner["id"]}
    ).json()
    task = client.post(
        "/api/tasks/",
        json={"title": "Setup env", "project_id": project["id"], "assignee_id": owner["id"]},
    ).json()

    response = client.post(
        f"/api/tasks/{task['id']}/comments",
        json={"content": "Note to self"},
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 201
    assert sent == []


def test_comment_on_unassigned_task_falls_back_to_project_owner(client, monkeypatch):
    sent = []
    monkeypatch.setattr(email, "send_email", lambda **kwargs: sent.append(kwargs))

    owner = _create_user(client, "owner", "owner@example.com")
    commenter = _create_user(client, "commenter", "commenter@example.com")
    project = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner["id"]}
    ).json()
    task = client.post(
        "/api/tasks/", json={"title": "Unassigned task", "project_id": project["id"]}
    ).json()

    response = client.post(
        f"/api/tasks/{task['id']}/comments",
        json={"content": "Who's picking this up?"},
        headers=_auth_headers(client, "commenter"),
    )
    assert response.status_code == 201
    assert len(sent) == 1
    assert sent[0]["to"] == "owner@example.com"
