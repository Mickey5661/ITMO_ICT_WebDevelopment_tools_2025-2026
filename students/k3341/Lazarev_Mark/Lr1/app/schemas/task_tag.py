from datetime import datetime
from pydantic import BaseModel


class TaskTagCreate(BaseModel):
    tag_id: int
    note: str | None = None  


class TaskTagRead(BaseModel):
    tag_id: int
    task_id: int
    note: str | None
    added_at: datetime

    model_config = {"from_attributes": True}
