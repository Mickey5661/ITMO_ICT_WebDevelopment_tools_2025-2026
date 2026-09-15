from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate, TaskReadDetailed
from app.schemas.task_tag import TaskTagCreate, TaskTagRead
from app.crud.task import (
    get_task, get_task_detailed, get_tasks, create_task,
    update_task, delete_task, add_tag_to_task, remove_tag_from_task,
)
from app.crud.tag import get_tag
from app.crud.category import get_category
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.get("/", response_model=list[TaskRead])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskRead]:
    """Получить все задачи текущего пользователя."""
    return get_tasks(db, owner_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_new_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    """Создать новую задачу."""
    # Категория необязательна, но если её прислали — она должна существовать
    # и принадлежать текущему пользователю. Без этой проверки несуществующий
    # category_id доходил до базы и падал 500-й ошибкой внешнего ключа.
    if data.category_id is not None and not get_category(db, data.category_id, current_user.id):
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return create_task(db, data, owner_id=current_user.id)


@router.get("/{task_id}", response_model=TaskReadDetailed)
def get_one_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskReadDetailed:
    """
    Получить задачу по ID с вложенными тегами и записями времени.
    Демонстрирует eager loading связей one-to-many и many-to-many.
    """
    task = get_task_detailed(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_one_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    """Обновить задачу (частичное обновление)."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if data.category_id is not None and not get_category(db, data.category_id, current_user.id):
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return update_task(db, task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Удалить задачу."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    delete_task(db, task)




@router.post("/{task_id}/tags", response_model=TaskTagRead, status_code=status.HTTP_201_CREATED)
def add_tag(
    task_id: int,
    data: TaskTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskTagRead:
    """Добавить тег к задаче."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if not get_tag(db, data.tag_id):
        raise HTTPException(status_code=404, detail="Тег не найден")
    return add_tag_to_task(db, task_id, data)


@router.delete("/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag(
    task_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Удалить тег у задачи."""
    task = get_task(db, task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if not remove_tag_from_task(db, task_id, tag_id):
        raise HTTPException(status_code=404, detail="Тег не прикреплён к задаче")
