from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.time_entry import (
    TimeEntryCreate, TimeEntryRead, TimeEntryUpdate, check_time_consistency,
)
from app.crud.time_entry import (
    get_time_entry, get_time_entries_for_task,
    create_time_entry, update_time_entry, delete_time_entry,
)
from app.crud.task import get_task
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/tasks/{task_id}/time-entries", tags=["Записи времени"])


@router.get("/", response_model=list[TimeEntryRead])
def list_time_entries(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TimeEntryRead]:
    """Получить все записи времени для задачи."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return get_time_entries_for_task(db, task_id)


@router.post("/", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
def create_entry(
    task_id: int,
    data: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TimeEntryRead:
    """Добавить запись о затраченном времени."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return create_time_entry(db, data, task_id=task_id)


@router.patch("/{entry_id}", response_model=TimeEntryRead)
def update_entry(
    task_id: int,
    entry_id: int,
    data: TimeEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TimeEntryRead:
    """Обновить запись времени."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    entry = get_time_entry(db, entry_id)
    if not entry or entry.task_id != task_id:
        raise HTTPException(status_code=404, detail="Запись времени не найдена")

    # PATCH может прислать только одно поле, поэтому проверяем не запрос сам по
    # себе, а то, что получится после слияния с уже сохранёнными значениями.
    # Иначе можно было бы поменять duration на 500 минут, не трогая даты.
    sent = data.model_fields_set
    merged_started = data.started_at if "started_at" in sent else entry.started_at
    merged_ended = data.ended_at if "ended_at" in sent else entry.ended_at
    merged_duration = data.duration_minutes if "duration_minutes" in sent else entry.duration_minutes
    try:
        check_time_consistency(merged_started, merged_ended, merged_duration)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return update_time_entry(db, entry, data)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    task_id: int,
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Удалить запись времени."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    entry = get_time_entry(db, entry_id)
    if not entry or entry.task_id != task_id:
        raise HTTPException(status_code=404, detail="Запись времени не найдена")
    delete_time_entry(db, entry)
