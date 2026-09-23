from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    return db.query(Task).offset(skip).limit(limit).all()


def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
