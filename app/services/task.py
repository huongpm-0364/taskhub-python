from sqlalchemy.orm import Session

from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.models.user import User
from app.repositories import comment, task
from app.schemas.task import TaskCreate, TaskCreateInProject


def get_task(db: Session, task_id: int) -> Task | None:
    return task.get_task(db, task_id)


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[Task]:
    return task.get_tasks(db, skip=skip, limit=limit, status=status, priority=priority)


def get_tasks_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
    return task.get_tasks_by_project(db, project_id, skip=skip, limit=limit)


def create_task(db: Session, payload: TaskCreate) -> Task:
    return task.create_task(
        db,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        project_id=payload.project_id,
        assignee_id=payload.assignee_id,
    )


def create_task_for_project(db: Session, project_id: int, payload: TaskCreateInProject) -> Task:
    return task.create_task(
        db,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        project_id=project_id,
        assignee_id=payload.assignee_id,
    )


def assign_task(db: Session, db_task: Task, *, assignee_id: int, actor: User) -> Task:
    """Reassigns a task and logs the change as a comment, as a single atomic write.

    Unlike the simpler repository methods elsewhere (which commit right after their own
    write), this bundles two writes — the assignee update and the audit comment — into
    one transaction: either both land or neither does, so the task's assignee never ends
    up out of sync with its own history. commits explicitly here instead of relying on
    app/repositories/comment.py's create_comment()'s caller-commits convention, and rolls
    back if anything goes wrong before the commit.
    """
    previous_assignee_id = db_task.assignee_id
    try:
        db_task.assignee_id = assignee_id
        db.add(db_task)
        comment.create_comment(
            db,
            content=_reassignment_note(previous_assignee_id, assignee_id, actor.username),
            task_id=db_task.id,
            author_id=actor.id,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_task)
    return db_task


def _reassignment_note(previous_assignee_id: int | None, new_assignee_id: int, actor_username: str) -> str:
    previous = f"user #{previous_assignee_id}" if previous_assignee_id is not None else "no one"
    return f"Reassigned from {previous} to user #{new_assignee_id} by {actor_username}."
