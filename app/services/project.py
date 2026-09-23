from sqlalchemy.orm import Session

from app import repositories
from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectHasTasksError(Exception):
    """Raised when trying to delete a project that still has tasks attached."""


def get_project(db: Session, project_id: int) -> Project | None:
    return repositories.project.get_project(db, project_id)


def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    owner_id: int | None = None,
) -> list[Project]:
    return repositories.project.get_projects(db, skip=skip, limit=limit, name=name, owner_id=owner_id)


def create_project(db: Session, project: ProjectCreate) -> Project:
    return repositories.project.create_project(
        db,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
    )


def delete_project(db: Session, db_project: Project) -> None:
    if db_project.tasks:
        raise ProjectHasTasksError(
            f"Project {db_project.id} still has {len(db_project.tasks)} task(s); "
            "move or delete them before deleting the project."
        )
    repositories.project.delete_project(db, db_project)
