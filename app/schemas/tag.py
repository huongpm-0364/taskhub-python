from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import TAG_NAME_MAX_LENGTH


class TagBase(BaseModel):
    name: str = Field(max_length=TAG_NAME_MAX_LENGTH)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=TAG_NAME_MAX_LENGTH)


class TagRead(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
