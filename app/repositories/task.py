from sqlalchemy.orm import Session

from app.models.enums import TaskStatus
from app.models.task import Task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    return db.query(Task).offset(skip).limit(limit).all()


def create_task(
    db: Session,
    *,
    title: str,
    description: str | None,
    status: TaskStatus,
    project_id: int,
    assignee_id: int | None,
) -> Task:
    db_task = Task(
        title=title,
        description=description,
        status=status,
        project_id=project_id,
        assignee_id=assignee_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
