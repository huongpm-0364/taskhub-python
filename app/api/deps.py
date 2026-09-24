import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import services
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.comment import Comment
from app.models.enums import UserRole
from app.models.project import Project
from app.models.task import Task
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    subject = payload.get("sub")
    if subject is None:
        raise credentials_exception
    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = services.user.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def verify_admin_role(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user


def verify_project_manager(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Project:
    """Fetches the project and checks that the caller may manage it.

    Declaring `project_id` here lets FastAPI pull it straight from the URL path of
    whichever route uses this dependency, so the route itself doesn't need to repeat it.
    """
    project = services.project.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role != UserRole.admin and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project's owner (or an admin) can perform this action",
        )
    return project


def verify_task_manager(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Task:
    """Like verify_project_manager, but for routes keyed by task_id instead of
    project_id (e.g. assigning a task) — resolves the task's project to check ownership.
    """
    task = services.task.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role != UserRole.admin and task.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the task's project manager (or an admin) can perform this action",
        )
    return task


def verify_comment_owner_or_manager(
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Comment:
    comment = services.comment.get_comment(db, comment_id)
    if comment is None or comment.task_id != task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    is_author = comment.author_id == current_user.id
    is_manager = current_user.role == UserRole.admin or comment.task.project.owner_id == current_user.id
    if not (is_author or is_manager):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the comment's author (or the task's project manager/admin) can perform this action",
        )
    return comment
