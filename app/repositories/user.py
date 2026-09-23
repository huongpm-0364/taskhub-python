from sqlalchemy.orm import Session, joinedload

from app.models.user import User


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_profile_by_username(db: Session, username: str) -> User | None:
    # joinedload of two different collections (projects, tasks) in one query multiplies
    # rows in the raw SQL result (a cartesian product between the two joins); SQLAlchemy's
    # identity map still collapses that correctly into one User with both collections
    # populated. Fine for a single-user lookup like this one — avoid the same combination
    # on a paginated list query (see repositories/task.py for why). Only used for the
    # profile endpoint; plain auth lookups use get_user_by_username() instead so a login
    # check doesn't pay for two extra joins it doesn't need.
    return (
        db.query(User)
        .options(joinedload(User.projects), joinedload(User.tasks))
        .filter(User.username == username)
        .first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, *, email: str, username: str, hashed_password: str) -> User:
    db_user = User(email=email, username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session,
    db_user: User,
    *,
    email: str | None,
    username: str | None,
    is_active: bool | None,
) -> User:
    if email is not None:
        db_user.email = email
    if username is not None:
        db_user.username = username
    if is_active is not None:
        db_user.is_active = is_active
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
