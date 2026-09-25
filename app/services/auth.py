from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User
from app.repositories import user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    db_user = user.get_user_by_username(db, username)
    if db_user is None or not verify_password(password, db_user.hashed_password):
        return None
    return db_user
