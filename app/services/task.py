from sqlalchemy.orm import Session

from app import repositories
from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskCreateInProject


def get_task(db: Session, task_id: int) -> Task | None:
    return repositories.task.get_task(db, task_id)


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[Task]:
    return repositories.task.get_tasks(db, skip=skip, limit=limit, status=status, priority=priority)


def get_tasks_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
    return repositories.task.get_tasks_by_project(db, project_id, skip=skip, limit=limit)


def create_task(db: Session, task: TaskCreate) -> Task:
    return repositories.task.create_task(
        db,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
    )


def create_task_for_project(db: Session, project_id: int, task: TaskCreateInProject) -> Task:
    return repositories.task.create_task(
        db,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        project_id=project_id,
        assignee_id=task.assignee_id,
    )


def assign_task(db: Session, task: Task, *, assignee_id: int, actor: User) -> Task:
    """Reassigns a task and logs the change as a comment, as a single atomic write.

    Unlike the simpler repository methods elsewhere (which commit right after their own
    write), this bundles two writes — the assignee update and the audit comment — into
    one transaction: either both land or neither does, so the task's assignee never ends
    up out of sync with its own history. commits explicitly here instead of relying on
    repositories.comment.create_comment()'s caller-commits convention, and rolls back if
    anything goes wrong before the commit.
    """
    previous_assignee_id = task.assignee_id
    try:
        task.assignee_id = assignee_id
        db.add(task)
        repositories.comment.create_comment(
            db,
            content=_reassignment_note(previous_assignee_id, assignee_id, actor.username),
            task_id=task.id,
            author_id=actor.id,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(task)
    return task


def _reassignment_note(previous_assignee_id: int | None, new_assignee_id: int, actor_username: str) -> str:
    previous = f"user #{previous_assignee_id}" if previous_assignee_id is not None else "no one"
    return f"Reassigned from {previous} to user #{new_assignee_id} by {actor_username}."
