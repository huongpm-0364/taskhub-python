from sqlalchemy.orm import Session, joinedload

from app.models.user import User


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    # joinedload of two different collections (projects, tasks) in one query multiplies
    # rows in the raw SQL result (a cartesian product between the two joins); SQLAlchemy's
    # identity map still collapses that correctly into one User with both collections
    # populated. Fine for a single-user lookup like this one — avoid the same combination
    # on a paginated list query (see repositories/task.py for why).
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
