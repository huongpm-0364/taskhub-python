import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import messages
from app.core.database import get_db
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.comment import Comment
from app.models.enums import UserRole
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.services import comment, project, task, user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = UnauthorizedError(
        messages.COULD_NOT_VALIDATE_CREDENTIALS, headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise credentials_error from exc

    subject = payload.get("sub")
    if subject is None:
        raise credentials_error
    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise credentials_error from exc

    db_user = user.get_user(db, user_id)
    if db_user is None:
        raise credentials_error
    return db_user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise BadRequestError(messages.INACTIVE_USER)
    return current_user


def verify_admin_role(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.admin:
        raise ForbiddenError(messages.ADMIN_ROLE_REQUIRED)
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
    db_project = project.get_project(db, project_id)
    if db_project is None:
        raise NotFoundError(messages.PROJECT_NOT_FOUND)
    if current_user.role != UserRole.admin and db_project.owner_id != current_user.id:
        raise ForbiddenError(messages.PROJECT_MANAGER_REQUIRED)
    return db_project


def verify_task_manager(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Task:
    """Like verify_project_manager, but for routes keyed by task_id instead of
    project_id (e.g. assigning a task) — resolves the task's project to check ownership.
    """
    db_task = task.get_task(db, task_id)
    if db_task is None:
        raise NotFoundError(messages.TASK_NOT_FOUND)
    if current_user.role != UserRole.admin and db_task.project.owner_id != current_user.id:
        raise ForbiddenError(messages.TASK_MANAGER_REQUIRED)
    return db_task


def verify_comment_owner_or_manager(
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Comment:
    db_comment = comment.get_comment(db, comment_id)
    if db_comment is None or db_comment.task_id != task_id:
        raise NotFoundError(messages.COMMENT_NOT_FOUND)
    is_author = db_comment.author_id == current_user.id
    is_manager = current_user.role == UserRole.admin or db_comment.task.project.owner_id == current_user.id
    if not (is_author or is_manager):
        raise ForbiddenError(messages.COMMENT_OWNER_OR_MANAGER_REQUIRED)
    return db_comment
