from sqlalchemy.orm import Session

from app import repositories
from app.models.comment import Comment


def get_comment(db: Session, comment_id: int) -> Comment | None:
    return repositories.comment.get_comment(db, comment_id)


def create_comment(db: Session, *, task_id: int, author_id: int, content: str) -> Comment:
    comment = repositories.comment.create_comment(db, content=content, task_id=task_id, author_id=author_id)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, db_comment: Comment, content: str) -> Comment:
    db_comment.content = content
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, db_comment: Comment) -> None:
    repositories.comment.delete_comment(db, db_comment)
    db.commit()
