from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import PROJECT_NAME_MAX_LENGTH


class ProjectBase(BaseModel):
    name: str = Field(max_length=PROJECT_NAME_MAX_LENGTH)
    description: str | None = None


class ProjectCreate(ProjectBase):
    owner_id: int


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=PROJECT_NAME_MAX_LENGTH)
    description: str | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
