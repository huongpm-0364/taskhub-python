from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import ConflictError
from app.models.project import Project
from app.repositories import project
from app.schemas.project import ProjectCreate


class ProjectHasTasksError(ConflictError):
    """Raised when trying to delete a project that still has tasks attached."""


def get_project(db: Session, project_id: int) -> Project | None:
    return project.get_project(db, project_id)


def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    owner_id: int | None = None,
) -> list[Project]:
    return project.get_projects(db, skip=skip, limit=limit, name=name, owner_id=owner_id)


def create_project(db: Session, payload: ProjectCreate) -> Project:
    return project.create_project(
        db,
        name=payload.name,
        description=payload.description,
        owner_id=payload.owner_id,
    )


def delete_project(db: Session, db_project: Project) -> None:
    if db_project.tasks:
        raise ProjectHasTasksError(
            messages.PROJECT_HAS_TASKS_TEMPLATE.format(
                project_id=db_project.id, task_count=len(db_project.tasks)
            )
        )
    project.delete_project(db, db_project)
