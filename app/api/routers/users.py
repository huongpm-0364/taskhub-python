from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import services
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT
from app.core.database import get_db
from app.schemas.user import UserCreate, UserProfile, UserRead

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    summary="List users",
)
def list_users(
    skip: int = Query(default=DEFAULT_SKIP, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return services.user.get_users(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return services.user.create_user(db, user)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get a user by id",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = services.user.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.get(
    "/{username}/profile",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get a user's profile by username",
    description="Returns the user together with the projects they own and the tasks assigned to them.",
)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    db_user = services.user.get_user_by_username(db, username)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user
