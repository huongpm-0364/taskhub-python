from sqlalchemy.orm import Session

from app import repositories
from app.models.bookmark import Bookmark


class BookmarkAlreadyExistsError(Exception):
    """Raised when the user already bookmarked this task."""


def create_bookmark(db: Session, *, user_id: int, task_id: int) -> Bookmark:
    if repositories.bookmark.get_bookmark(db, user_id, task_id) is not None:
        raise BookmarkAlreadyExistsError("Task already bookmarked")
    return repositories.bookmark.create_bookmark(db, user_id=user_id, task_id=task_id)
