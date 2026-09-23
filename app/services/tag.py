from sqlalchemy.orm import Session

from app import repositories
from app.models.tag import Tag
from app.schemas.tag import TagCreate


def get_tag(db: Session, tag_id: int) -> Tag | None:
    return repositories.tag.get_tag(db, tag_id)


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> list[Tag]:
    return repositories.tag.get_tags(db, skip=skip, limit=limit)


def create_tag(db: Session, tag: TagCreate) -> Tag:
    return repositories.tag.create_tag(db, name=tag.name)
