from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import services
from app.api.deps import get_current_active_user, verify_comment_owner_or_manager, verify_task_manager
from app.core.database import get_db
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT
from app.models.comment import Comment
from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.models.user import User
from app.schemas.bookmark import BookmarkRead
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.schemas.task import TaskAssign, TaskCreate, TaskRead
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
    "/{task_id}/assign",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Assign a task to a user",
    description=(
        "Only the task's project manager (or an admin) can do this. "
        "Records the reassignment as a comment, atomically with the assignee change."
    ),
)
def assign_task(
    payload: TaskAssign,
    task: Task = Depends(verify_task_manager),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if services.user.get_user(db, payload.assignee_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
    return services.task.assign_task(db, task, assignee_id=payload.assignee_id, actor=current_user)


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


@router.post(
    "/{task_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a task",
    description="Requires being logged in.",
)
def create_comment(
    task_id: int,
    payload: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if services.task.get_task(db, task_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return services.comment.create_comment(
        db, task_id=task_id, author_id=current_user.id, content=payload.content
    )


@router.put(
    "/{task_id}/comments/{comment_id}",
    response_model=CommentRead,
    status_code=status.HTTP_200_OK,
    summary="Edit a comment",
    description="Only the comment's author (or the task's project manager/admin) can do this.",
)
def update_comment(
    payload: CommentUpdate,
    comment: Comment = Depends(verify_comment_owner_or_manager),
    db: Session = Depends(get_db),
):
    return services.comment.update_comment(db, comment, payload.content)


@router.delete(
    "/{task_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment",
    description="Only the comment's author (or the task's project manager/admin) can do this.",
)
def delete_comment(
    comment: Comment = Depends(verify_comment_owner_or_manager),
    db: Session = Depends(get_db),
):
    services.comment.delete_comment(db, comment)
