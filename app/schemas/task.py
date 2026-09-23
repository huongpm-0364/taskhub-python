from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import TASK_TITLE_MAX_LENGTH
from app.models.enums import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(max_length=TASK_TITLE_MAX_LENGTH)
    description: str | None = None
    status: TaskStatus = TaskStatus.todo


class TaskCreate(TaskBase):
    project_id: int
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=TASK_TITLE_MAX_LENGTH)
    description: str | None = None
    status: TaskStatus | None = None
    assignee_id: int | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    assignee_id: int | None = None
    created_at: datetime
    updated_at: datetime
