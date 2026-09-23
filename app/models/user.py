from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    USER_EMAIL_MAX_LENGTH,
    USER_HASHED_PASSWORD_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from app.core.database import Base
from app.models.enums import UserRole

__all__ = ["User", "UserRole"]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(USER_EMAIL_MAX_LENGTH), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(USER_HASHED_PASSWORD_MAX_LENGTH), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Not exposed on UserCreate/UserUpdate on purpose: only the ORM default (member) is
    # reachable through the public API, so self-registration/self-update can never grant
    # admin. Promoting someone to admin currently has to happen directly in the database.
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.member, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    projects: Mapped[list["Project"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="assignee")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author", cascade="all, delete-orphan")
