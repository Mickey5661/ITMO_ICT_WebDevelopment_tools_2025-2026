from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TaskTag(Base):

    __tablename__ = "task_tags"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task: Mapped["Task"] = relationship("Task", back_populates="tag_associations")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="task_associations")
