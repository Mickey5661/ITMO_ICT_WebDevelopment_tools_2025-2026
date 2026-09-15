from sqlalchemy.orm import Session, joinedload
from app.models.task import Task
from app.models.task_tag import TaskTag
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.task_tag import TaskTagCreate


def get_task(db: Session, task_id: int, owner_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id, Task.owner_id == owner_id).first()


def get_task_detailed(db: Session, task_id: int, owner_id: int) -> Task | None:
    """Получить задачу"""
    return (
        db.query(Task)
        .options(
            joinedload(Task.tag_associations).joinedload(TaskTag.tag),
            joinedload(Task.time_entries),
        )
        .filter(Task.id == task_id, Task.owner_id == owner_id)
        .first()
    )


def get_tasks(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
    return db.query(Task).filter(Task.owner_id == owner_id).offset(skip).limit(limit).all()


def create_task(db: Session, data: TaskCreate, owner_id: int) -> Task:
    task = Task(**data.model_dump(), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def add_tag_to_task(db: Session, task_id: int, data: TaskTagCreate) -> TaskTag:
    """Добавить тег к задаче с опциональной заметкой (many-to-many)."""
    association = TaskTag(task_id=task_id, tag_id=data.tag_id, note=data.note)
    db.add(association)
    db.commit()
    db.refresh(association)
    return association


def remove_tag_from_task(db: Session, task_id: int, tag_id: int) -> bool:
    """Удалить тег у задачи. Возвращает True если запись была найдена."""
    association = db.query(TaskTag).filter(
        TaskTag.task_id == task_id, TaskTag.tag_id == tag_id
    ).first()
    if not association:
        return False
    db.delete(association)
    db.commit()
    return True
