from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core import messages
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT
from app.schemas.tag import TagCreate, TagRead
from app.services import tag

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get(
    "/",
    response_model=list[TagRead],
    status_code=status.HTTP_200_OK,
    summary="List tags",
)
def list_tags(
    skip: int = Query(default=DEFAULT_SKIP, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return tag.get_tags(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tag",
)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    return tag.create_tag(db, payload)


@router.get(
    "/{tag_id}",
    response_model=TagRead,
    status_code=status.HTTP_200_OK,
    summary="Get a tag by id",
)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = tag.get_tag(db, tag_id)
    if db_tag is None:
        raise NotFoundError(messages.TAG_NOT_FOUND)
    return db_tag
