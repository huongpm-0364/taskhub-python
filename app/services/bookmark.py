from sqlalchemy.orm import Session

from app.core import messages
from app.core.exceptions import ConflictError
from app.models.bookmark import Bookmark
from app.repositories import bookmark


class BookmarkAlreadyExistsError(ConflictError):
    """Raised when the user already bookmarked this task."""


def create_bookmark(db: Session, *, user_id: int, task_id: int) -> Bookmark:
    if bookmark.get_bookmark(db, user_id, task_id) is not None:
        raise BookmarkAlreadyExistsError(messages.TASK_ALREADY_BOOKMARKED)
    return bookmark.create_bookmark(db, user_id=user_id, task_id=task_id)
