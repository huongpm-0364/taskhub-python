from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate


def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> list[Project]:
    return db.query(Project).offset(skip).limit(limit).all()


def create_project(db: Session, project: ProjectCreate) -> Project:
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project
