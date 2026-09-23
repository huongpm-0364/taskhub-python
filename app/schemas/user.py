from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import USERNAME_MAX_LENGTH
from app.schemas.project import ProjectRead
from app.schemas.task import TaskRead


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(max_length=USERNAME_MAX_LENGTH)


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, max_length=USERNAME_MAX_LENGTH)
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class UserProfile(UserRead):
    projects: list[ProjectRead] = []
    tasks: list[TaskRead] = []
