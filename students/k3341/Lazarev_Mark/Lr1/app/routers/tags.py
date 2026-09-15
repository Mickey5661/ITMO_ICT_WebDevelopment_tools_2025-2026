from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.tag import TagCreate, TagRead
from app.crud.tag import get_tag, get_tag_by_name, get_tags, create_tag, delete_tag
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/tags", tags=["Теги"])


@router.get("/", response_model=list[TagRead])
def list_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[TagRead]:
    """Получить все теги."""
    return get_tags(db, skip=skip, limit=limit)


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_new_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TagRead:
    """Создать новый тег."""
    if get_tag_by_name(db, data.name):
        raise HTTPException(status_code=400, detail="Тег с таким именем уже существует")
    return create_tag(db, data)


@router.get("/{tag_id}", response_model=TagRead)
def get_one_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TagRead:
    """Получить тег по ID."""
    tag = get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Тег не найден")
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> None:
    """Удалить тег."""
    tag = get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Тег не найден")
    delete_tag(db, tag)
