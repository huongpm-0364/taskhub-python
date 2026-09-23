import bcrypt
from sqlalchemy.orm import Session

from app import repositories
from app.models.user import User
from app.schemas.user import UserCreate


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_user(db: Session, user_id: int) -> User | None:
    return repositories.user.get_user(db, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return repositories.user.get_user_by_username(db, username)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return repositories.user.get_users(db, skip=skip, limit=limit)


def create_user(db: Session, user: UserCreate) -> User:
    return repositories.user.create_user(
        db,
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
    )
