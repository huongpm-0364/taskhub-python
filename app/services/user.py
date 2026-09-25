from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user
from app.schemas.user import UserCreate, UserUpdate


class UserAlreadyExistsError(ConflictError):
    """Raised when the email or username is already taken."""


def get_user(db: Session, user_id: int) -> User | None:
    return user.get_user(db, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return user.get_user_by_username(db, username)


def get_user_profile_by_username(db: Session, username: str) -> User | None:
    return user.get_user_profile_by_username(db, username)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return user.get_users(db, skip=skip, limit=limit)


def create_user(db: Session, payload: UserCreate) -> User:
    try:
        return user.create_user(
            db,
            email=payload.email,
            username=payload.username,
            hashed_password=hash_password(payload.password),
        )
    except IntegrityError as exc:
        db.rollback()
        raise UserAlreadyExistsError(messages.EMAIL_OR_USERNAME_ALREADY_REGISTERED) from exc


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    try:
        return user.update_user(
            db,
            db_user,
            email=user_update.email,
            username=user_update.username,
            is_active=user_update.is_active,
        )
    except IntegrityError as exc:
        db.rollback()
        raise UserAlreadyExistsError(messages.EMAIL_OR_USERNAME_ALREADY_TAKEN) from exc
