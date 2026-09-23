from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookmarkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    task_id: int
    created_at: datetime
