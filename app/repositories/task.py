from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id, options=[joinedload(Task.tags)])


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[Task]:
    # selectinload, not joinedload: Task.tags is a many-to-many collection, and joining a
    # collection together with LIMIT/OFFSET on the parent query can silently truncate
    # results (the LIMIT counts joined rows, not distinct tasks). selectinload runs a
    # second `WHERE task_id IN (...)` query against the already-paginated task ids instead,
    # which stays correct and still avoids N+1 (2 queries total, not 1-per-task).
    query = db.query(Task).options(selectinload(Task.tags))
    if status is not None:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    # order_by is required for skip/limit to be meaningful: without an explicit order,
    # SQL doesn't guarantee row order, so pagination could return inconsistent results
    # (duplicates or gaps) between calls.
    return query.order_by(Task.id).offset(skip).limit(limit).all()


def get_tasks_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
    return (
        db.query(Task)
        .options(selectinload(Task.tags))
        .filter(Task.project_id == project_id)
        .order_by(Task.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_task(
    db: Session,
    *,
    title: str,
    description: str | None,
    status: TaskStatus,
    priority: TaskPriority,
    project_id: int,
    assignee_id: int | None,
) -> Task:
    db_task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        project_id=project_id,
        assignee_id=assignee_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
