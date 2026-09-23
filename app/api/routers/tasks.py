from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT
from app.models.enums import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.bookmark import BookmarkRead
from app.schemas.task import TaskCreate, TaskRead
from app.services.bookmark import BookmarkAlreadyExistsError

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get(
    "/",
    response_model=list[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="List tasks",
    description="Optionally filtered by status and/or priority.",
)
def list_tasks(
    skip: int = Query(default=DEFAULT_SKIP, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    status: TaskStatus | None = Query(default=None, description="Filter by task status"),
    priority: TaskPriority | None = Query(default=None, description="Filter by task priority"),
    db: Session = Depends(get_db),
):
    return services.task.get_tasks(db, skip=skip, limit=limit, status=status, priority=priority)


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return services.task.create_task(db, task)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Get a task by id",
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    db_task = services.task.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.post(
    "/{task_id}/bookmark",
    response_model=BookmarkRead,
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark a task",
    description="Requires being logged in.",
)
def bookmark_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if services.task.get_task(db, task_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    try:
        return services.bookmark.create_bookmark(db, user_id=current_user.id, task_id=task_id)
    except BookmarkAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
