from sqlalchemy.orm import Session

from app import repositories
from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
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
