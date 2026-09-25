from sqlalchemy.orm import Session

from app.core import cache
from app.core.constants import TAGS_CACHE_KEY, TAGS_CACHE_TTL_SECONDS
from app.models.tag import Tag
from app.repositories import tag
from app.schemas.tag import TagCreate, TagRead


def get_tag(db: Session, tag_id: int) -> Tag | None:
    return tag.get_tag(db, tag_id)


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> list[TagRead]:
    # Unlike every other service function, this returns schema objects (TagRead) rather
    # than ORM models: a cache hit never touches the DB, so there's no ORM instance to
    # hand back on that path, only whatever JSON came out of Redis. Returning TagRead
    # either way keeps the return type consistent regardless of cache hit/miss.
    #
    # Tags are cached as one unpaginated list (they're a small, rarely-changing
    # reference list), and skip/limit are applied in Python after reading the cache.
    cached = cache.get_json(TAGS_CACHE_KEY)
    if cached is None:
        all_tags = tag.get_all_tags(db)
        cached = [TagRead.model_validate(t).model_dump(mode="json") for t in all_tags]
        cache.set_json(TAGS_CACHE_KEY, cached, ttl_seconds=TAGS_CACHE_TTL_SECONDS)
    return [TagRead(**item) for item in cached[skip : skip + limit]]


def create_tag(db: Session, payload: TagCreate) -> Tag:
    db_tag = tag.create_tag(db, name=payload.name)
    cache.delete(TAGS_CACHE_KEY)
    return db_tag
