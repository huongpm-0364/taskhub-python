from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import services
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT
from app.core.database import get_db
from app.schemas.tag import TagCreate, TagRead

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
    return services.tag.get_tags(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tag",
)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    return services.tag.create_tag(db, tag)


@router.get(
    "/{tag_id}",
    response_model=TagRead,
    status_code=status.HTTP_200_OK,
    summary="Get a tag by id",
)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = services.tag.get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return db_tag
