from sqlalchemy.orm import Session, joinedload

from app.models.project import Project


def get_project(db: Session, project_id: int) -> Project | None:
    # joinedload is safe here: this fetches a single project by primary key, so there's no
    # LIMIT/OFFSET for the collection join to interact badly with (see repositories/task.py
    # for the case where that does matter).
    return db.get(Project, project_id, options=[joinedload(Project.tasks)])


def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    owner_id: int | None = None,
) -> list[Project]:
    query = db.query(Project)
    if name:
        query = query.filter(Project.name.ilike(f"%{name}%"))
    if owner_id is not None:
        query = query.filter(Project.owner_id == owner_id)
    return query.order_by(Project.id).offset(skip).limit(limit).all()


def create_project(db: Session, *, name: str, description: str | None, owner_id: int) -> Project:
    db_project = Project(name=name, description=description, owner_id=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, db_project: Project) -> None:
    db.delete(db_project)
    db.commit()
