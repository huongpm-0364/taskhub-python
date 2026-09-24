from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import verify_project_manager
from app.core.database import get_db
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectWithTasks
from app.schemas.task import TaskCreateInProject, TaskRead
from app.services.project import ProjectHasTasksError

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get(
    "/",
    response_model=list[ProjectRead],
    status_code=status.HTTP_200_OK,
    summary="List projects",
    description="List projects, optionally filtered by name (partial match) and/or owner.",
)
def list_projects(
    skip: int = Query(default=DEFAULT_SKIP, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    name: str | None = Query(default=None, description="Filter by project name (partial match)"),
    owner_id: int | None = Query(default=None, description="Filter by owner id"),
    db: Session = Depends(get_db),
):
    return services.project.get_projects(db, skip=skip, limit=limit, name=name, owner_id=owner_id)


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    return services.project.create_project(db, project)


@router.get(
    "/{project_id}",
    response_model=ProjectWithTasks,
    status_code=status.HTTP_200_OK,
    summary="Get a project by id",
    description="Returns the project together with its list of tasks.",
)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = services.project.get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return db_project


@router.get(
    "/{project_id}/tasks",
    response_model=list[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="List tasks in a project",
)
def list_project_tasks(
    project_id: int,
    skip: int = Query(default=DEFAULT_SKIP, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    if services.project.get_project(db, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return services.task.get_tasks_by_project(db, project_id, skip=skip, limit=limit)


@router.post(
    "/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task in a project",
)
def create_project_task(project_id: int, task: TaskCreateInProject, db: Session = Depends(get_db)):
    if services.project.get_project(db, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return services.task.create_task_for_project(db, project_id, task)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description=(
        "Only the project's owner (or an admin) can delete it. "
        "Fails with 409 if the project still has tasks attached."
    ),
)
def delete_project(
    db: Session = Depends(get_db),
    db_project: Project = Depends(verify_project_manager),
):
    try:
        services.project.delete_project(db, db_project)
    except ProjectHasTasksError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
