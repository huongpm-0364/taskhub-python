from sqlalchemy.orm import Session

from app import repositories
from app.models.task import Task
from app.schemas.task import TaskCreate


def get_task(db: Session, task_id: int) -> Task | None:
    return repositories.task.get_task(db, task_id)


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    return repositories.task.get_tasks(db, skip=skip, limit=limit)


def create_task(db: Session, task: TaskCreate) -> Task:
    return repositories.task.create_task(
        db,
        title=task.title,
        description=task.description,
        status=task.status,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
    )
