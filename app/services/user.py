from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import repositories
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserAlreadyExistsError(Exception):
    """Raised when the email or username is already taken."""


def get_user(db: Session, user_id: int) -> User | None:
    return repositories.user.get_user(db, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return repositories.user.get_user_by_username(db, username)


def get_user_profile_by_username(db: Session, username: str) -> User | None:
    return repositories.user.get_user_profile_by_username(db, username)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return repositories.user.get_users(db, skip=skip, limit=limit)


def create_user(db: Session, user: UserCreate) -> User:
    try:
        return repositories.user.create_user(
            db,
            email=user.email,
            username=user.username,
            hashed_password=hash_password(user.password),
        )
    except IntegrityError as exc:
        db.rollback()
        raise UserAlreadyExistsError("Email or username already registered") from exc


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    try:
        return repositories.user.update_user(
            db,
            db_user,
            email=user_update.email,
            username=user_update.username,
            is_active=user_update.is_active,
        )
    except IntegrityError as exc:
        db.rollback()
        raise UserAlreadyExistsError("Email or username already taken") from exc
