def _create_user(client, username="owner", email="owner@example.com", password="secret123") -> int:
    return client.post(
        "/api/users/",
        json={"email": email, "username": username, "password": password},
    ).json()["id"]


def _login(client, username, password="secret123") -> str:
    return client.post(
        "/api/users/login", data={"username": username, "password": password}
    ).json()["access_token"]


def _auth_headers(client, username, password="secret123") -> dict:
    return {"Authorization": f"Bearer {_login(client, username, password)}"}


def _create_project_and_task(client, owner_username="owner") -> tuple[int, int]:
    owner_id = _create_user(client, username=owner_username, email=f"{owner_username}@example.com")
    project_id = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id}
    ).json()["id"]
    task_id = client.post(
        "/api/tasks/", json={"title": "Setup env", "project_id": project_id}
    ).json()["id"]
    return owner_id, task_id


def test_create_comment_requires_auth(client):
    _, task_id = _create_project_and_task(client)

    response = client.post(f"/api/tasks/{task_id}/comments", json={"content": "hi"})
    assert response.status_code == 401


def test_create_comment(client):
    _, task_id = _create_project_and_task(client)

    response = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "Looks good to me"},
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Looks good to me"
    assert data["task_id"] == task_id


def test_create_comment_task_not_found(client):
    _create_user(client)
    response = client.post(
        "/api/tasks/999/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 404


def test_author_can_delete_own_comment(client):
    _, task_id = _create_project_and_task(client)
    _create_user(client, username="commenter", email="commenter@example.com")
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "commenter"),
    ).json()["id"]

    response = client.delete(
        f"/api/tasks/{task_id}/comments/{comment_id}",
        headers=_auth_headers(client, "commenter"),
    )
    assert response.status_code == 204


def test_stranger_cannot_delete_someone_elses_comment(client):
    _, task_id = _create_project_and_task(client)
    _create_user(client, username="commenter", email="commenter@example.com")
    _create_user(client, username="stranger", email="stranger@example.com")
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "commenter"),
    ).json()["id"]

    response = client.delete(
        f"/api/tasks/{task_id}/comments/{comment_id}",
        headers=_auth_headers(client, "stranger"),
    )
    assert response.status_code == 403


def test_project_manager_can_delete_others_comment(client):
    owner_id, task_id = _create_project_and_task(client)
    _create_user(client, username="commenter", email="commenter@example.com")
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "commenter"),
    ).json()["id"]

    response = client.delete(
        f"/api/tasks/{task_id}/comments/{comment_id}",
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 204


def test_admin_can_delete_any_comment(client, db_session):
    from app.models.enums import UserRole
    from app.models.user import User

    _, task_id = _create_project_and_task(client)
    _create_user(client, username="commenter", email="commenter@example.com")
    _create_user(client, username="root", email="root@example.com")
    admin = db_session.query(User).filter(User.username == "root").first()
    admin.role = UserRole.admin
    db_session.commit()
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "commenter"),
    ).json()["id"]

    response = client.delete(
        f"/api/tasks/{task_id}/comments/{comment_id}",
        headers=_auth_headers(client, "root"),
    )
    assert response.status_code == 204


def test_delete_comment_wrong_task_id_is_not_found(client):
    _, task_id = _create_project_and_task(client)
    _, other_task_id = _create_project_and_task(client, owner_username="owner2")
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "owner"),
    ).json()["id"]

    response = client.delete(
        f"/api/tasks/{other_task_id}/comments/{comment_id}",
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 404


def test_author_can_edit_own_comment(client):
    _, task_id = _create_project_and_task(client)
    _create_user(client, username="commenter", email="commenter@example.com")
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "commenter"),
    ).json()["id"]

    response = client.put(
        f"/api/tasks/{task_id}/comments/{comment_id}",
        json={"content": "edited"},
        headers=_auth_headers(client, "commenter"),
    )
    assert response.status_code == 200
    assert response.json()["content"] == "edited"


def test_stranger_cannot_edit_someone_elses_comment(client):
    _, task_id = _create_project_and_task(client)
    _create_user(client, username="commenter", email="commenter@example.com")
    _create_user(client, username="stranger", email="stranger@example.com")
    comment_id = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "hi"},
        headers=_auth_headers(client, "commenter"),
    ).json()["id"]

    response = client.put(
        f"/api/tasks/{task_id}/comments/{comment_id}",
        json={"content": "hijacked"},
        headers=_auth_headers(client, "stranger"),
    )
    assert response.status_code == 403
