from sqlalchemy.orm import Session
from app.models.time_entry import TimeEntry
from app.schemas.time_entry import TimeEntryCreate, TimeEntryUpdate


def get_time_entry(db: Session, entry_id: int) -> TimeEntry | None:
    return db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()


def get_time_entries_for_task(db: Session, task_id: int) -> list[TimeEntry]:
    return db.query(TimeEntry).filter(TimeEntry.task_id == task_id).all()


def create_time_entry(db: Session, data: TimeEntryCreate, task_id: int) -> TimeEntry:
    entry = TimeEntry(**data.model_dump(), task_id=task_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_time_entry(db: Session, entry: TimeEntry, data: TimeEntryUpdate) -> TimeEntry:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_time_entry(db: Session, entry: TimeEntry) -> None:
    db.delete(entry)
    db.commit()
