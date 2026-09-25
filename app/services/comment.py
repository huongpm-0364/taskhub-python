from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.repositories import comment
from app.services import notifications


def get_comment(db: Session, comment_id: int) -> Comment | None:
    return comment.get_comment(db, comment_id)


def create_comment_for_task(
    db: Session,
    background_tasks: BackgroundTasks,
    *,
    db_task: Task,
    author: User,
    content: str,
) -> Comment:
    """Creates a comment on `db_task` and schedules its notification as one unit.

    The insert and the notification dispatch are the two things that always need to
    happen together when someone comments — bundling them here (instead of leaving the
    router to call both separately) means the DB write commits exactly once and any
    future caller gets the notification for free, instead of having to remember to
    wire it up itself.
    """
    db_comment = comment.create_comment(db, content=content, task_id=db_task.id, author_id=author.id)
    db.commit()
    db.refresh(db_comment)
    notifications.notify_new_comment(background_tasks, task=db_task, comment=db_comment, author=author)
    return db_comment


def update_comment(db: Session, db_comment: Comment, content: str) -> Comment:
    db_comment.content = content
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, db_comment: Comment) -> None:
    comment.delete_comment(db, db_comment)
    db.commit()
