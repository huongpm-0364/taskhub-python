from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import USERNAME_MAX_LENGTH


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
