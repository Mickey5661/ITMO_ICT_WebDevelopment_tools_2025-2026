from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.medium)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.todo)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)  
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    
    owner: Mapped["User"] = relationship("User", back_populates="tasks")
    category: Mapped["Category | None"] = relationship("Category", back_populates="tasks")

    
    tag_associations: Mapped[list["TaskTag"]] = relationship(
        "TaskTag", back_populates="task", cascade="all, delete-orphan"
    )
    
    time_entries: Mapped[list["TimeEntry"]] = relationship(
        "TimeEntry", back_populates="task", cascade="all, delete-orphan"
    )
