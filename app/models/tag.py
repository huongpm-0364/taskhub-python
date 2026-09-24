from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import TAG_NAME_MAX_LENGTH
from app.core.database import Base
from app.models.associations import task_tags


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(TAG_NAME_MAX_LENGTH), unique=True, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(secondary=task_tags, back_populates="tags")
