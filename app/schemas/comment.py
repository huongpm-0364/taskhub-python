from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import COMMENT_CONTENT_MAX_LENGTH


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=COMMENT_CONTENT_MAX_LENGTH)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=COMMENT_CONTENT_MAX_LENGTH)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    task_id: int
    author_id: int
    created_at: datetime
