from sqlalchemy.orm import Session

from app import repositories
from app.core.security import verify_password
from app.models.user import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = repositories.user.get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
