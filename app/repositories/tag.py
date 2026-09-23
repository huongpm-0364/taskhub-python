from sqlalchemy.orm import Session

from app.models.tag import Tag


def get_tag(db: Session, tag_id: int) -> Tag | None:
    return db.get(Tag, tag_id)


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> list[Tag]:
    return db.query(Tag).order_by(Tag.id).offset(skip).limit(limit).all()


def create_tag(db: Session, *, name: str) -> Tag:
    db_tag = Tag(name=name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag
