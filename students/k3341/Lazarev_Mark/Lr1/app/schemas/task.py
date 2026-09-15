from datetime import datetime
from pydantic import BaseModel, Field
from app.models.task import Priority, TaskStatus
from app.schemas.tag import TagRead
from app.schemas.time_entry import TimeEntryRead
from app.schemas.task_tag import TaskTagRead


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: Priority = Priority.medium
    status: TaskStatus = TaskStatus.todo
    deadline: datetime | None = None
    estimated_minutes: int | None = Field(None, gt=0)
    category_id: int | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    priority: Priority
    status: TaskStatus
    deadline: datetime | None
    estimated_minutes: int | None
    created_at: datetime
    updated_at: datetime
    owner_id: int
    category_id: int | None

    model_config = {"from_attributes": True}


class TaskReadDetailed(TaskRead):
    """Задача с вложенными тегами и записями времени (для GET с joins)."""
    tag_associations: list[TaskTagRead] = []
    time_entries: list[TimeEntryRead] = []

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None
    deadline: datetime | None = None
    estimated_minutes: int | None = Field(None, gt=0)
    category_id: int | None = None
