import pytest


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


def _create_project_and_task(client, owner_username="owner") -> tuple[int, int, int]:
    owner_id = _create_user(client, username=owner_username, email=f"{owner_username}@example.com")
    project_id = client.post(
        "/api/projects/", json={"name": "TaskHub Core", "owner_id": owner_id}
    ).json()["id"]
    task_id = client.post(
        "/api/tasks/", json={"title": "Setup env", "project_id": project_id}
    ).json()["id"]
    return owner_id, project_id, task_id


def test_assign_task_requires_auth(client):
    _, _, task_id = _create_project_and_task(client)

    response = client.post(f"/api/tasks/{task_id}/assign", json={"assignee_id": 1})
    assert response.status_code == 401


def test_assign_task_by_non_manager_is_forbidden(client):
    owner_id, project_id, task_id = _create_project_and_task(client)
    _create_user(client, username="intruder", email="intruder@example.com")

    response = client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": owner_id},
        headers=_auth_headers(client, "intruder"),
    )
    assert response.status_code == 403


def test_assign_task_not_found(client):
    _create_user(client)
    response = client.post(
        "/api/tasks/999/assign",
        json={"assignee_id": 1},
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 404


def test_assign_task_unknown_assignee(client):
    owner_id, project_id, task_id = _create_project_and_task(client)

    response = client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": 999},
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 404


def test_assign_task_success_updates_assignee_and_logs_comment(client, db_session):
    from app.models.comment import Comment

    owner_id, project_id, task_id = _create_project_and_task(client)
    assignee_id = _create_user(client, username="dev", email="dev@example.com")

    response = client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": assignee_id},
        headers=_auth_headers(client, "owner"),
    )
    assert response.status_code == 200
    assert response.json()["assignee_id"] == assignee_id

    # the reassignment must be logged atomically as a comment on the task — there's no
    # "list comments" endpoint yet, so check the row directly.
    comments = db_session.query(Comment).filter(Comment.task_id == task_id).all()
    assert len(comments) == 1
    assert "Reassigned" in comments[0].content
    assert comments[0].author_id == owner_id


def test_reassign_task_logs_a_second_comment(client, db_session):
    from app.models.comment import Comment

    owner_id, project_id, task_id = _create_project_and_task(client)
    first_assignee_id = _create_user(client, username="dev1", email="dev1@example.com")
    second_assignee_id = _create_user(client, username="dev2", email="dev2@example.com")

    client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": first_assignee_id},
        headers=_auth_headers(client, "owner"),
    )
    client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": second_assignee_id},
        headers=_auth_headers(client, "owner"),
    )

    comments = db_session.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.id).all()
    assert len(comments) == 2
    assert "no one" in comments[0].content
    assert f"user #{first_assignee_id}" in comments[1].content


def test_assign_task_rolls_back_assignee_change_if_comment_insert_fails(client, db_session, monkeypatch):
    """Proves assign_task is one atomic transaction, not two independent writes.

    If logging the reassignment as a comment fails partway through, the assignee change
    must not stick either — otherwise the task's assignee and its own history would
    silently disagree.
    """
    from app.models.task import Task
    from app.repositories import comment

    owner_id, project_id, task_id = _create_project_and_task(client)
    assignee_id = _create_user(client, username="dev", email="dev@example.com")

    def boom(*args, **kwargs):
        raise RuntimeError("simulated failure while writing the audit comment")

    monkeypatch.setattr(comment, "create_comment", boom)

    with pytest.raises(RuntimeError):
        client.post(
            f"/api/tasks/{task_id}/assign",
            json={"assignee_id": assignee_id},
            headers=_auth_headers(client, "owner"),
        )

    db_session.rollback()
    db_session.expire_all()
    task = db_session.get(Task, task_id)
    assert task.assignee_id is None


def test_admin_can_assign_task_in_any_project(client, db_session):
    from app.models.enums import UserRole
    from app.models.user import User

    owner_id, project_id, task_id = _create_project_and_task(client)
    assignee_id = _create_user(client, username="dev", email="dev@example.com")
    _create_user(client, username="root", email="root@example.com")
    admin = db_session.query(User).filter(User.username == "root").first()
    admin.role = UserRole.admin
    db_session.commit()

    response = client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": assignee_id},
        headers=_auth_headers(client, "root"),
    )
    assert response.status_code == 200
