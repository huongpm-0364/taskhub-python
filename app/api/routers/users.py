from datetime import timedelta

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, verify_admin_role
from app.core import messages
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_SKIP, MAX_LIMIT
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserProfile, UserRead, UserUpdate
from app.services import auth, user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Admin only.",
)
def list_users(
    skip: int = Query(default=DEFAULT_SKIP, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
    _admin: User = Depends(verify_admin_role),
):
    return user.get_users(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return user.create_user(db, payload)


# NOTE: literal routes below (/register, /login, /me) must stay registered before
# "/{user_id}" — Starlette matches routes in registration order using a plain string
# converter for "{user_id}", so a request to "/me" would otherwise match "/{user_id}"
# first and fail Pydantic's int conversion instead of reaching this route.
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return user.create_user(db, payload)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Log in and get an access token",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, form_data.username, form_data.password)
    if db_user is None:
        raise UnauthorizedError(
            messages.INCORRECT_USERNAME_OR_PASSWORD, headers={"WWW-Authenticate": "Bearer"}
        )
    # subject is the user's id, not username: the id never changes, so renaming a
    # username later (PUT /me) doesn't invalidate tokens already issued for that account.
    access_token = create_access_token(
        subject=str(db_user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token)


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get the current logged-in user",
)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update the current logged-in user",
)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return user.update_user(db, current_user, user_update)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get a user by id",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user.get_user(db, user_id)
    if db_user is None:
        raise NotFoundError(messages.USER_NOT_FOUND)
    return db_user


@router.get(
    "/{username}/profile",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get a user's profile by username",
    description="Returns the user together with the projects they own and the tasks assigned to them.",
)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    db_user = user.get_user_profile_by_username(db, username)
    if db_user is None:
        raise NotFoundError(messages.USER_NOT_FOUND)
    return db_user
