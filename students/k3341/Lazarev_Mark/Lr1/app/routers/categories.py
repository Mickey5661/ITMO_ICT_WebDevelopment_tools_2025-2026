from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.crud.category import get_category, get_categories, create_category, update_category, delete_category
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/categories", tags=["Категории"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CategoryRead]:
    """Получить все категории текущего пользователя."""
    return get_categories(db, owner_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_new_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    """Создать новую категорию."""
    return create_category(db, data, owner_id=current_user.id)


@router.get("/{category_id}", response_model=CategoryRead)
def get_one_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    """Получить категорию по ID."""
    category = get_category(db, category_id, owner_id=current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_one_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    """Обновить категорию."""
    category = get_category(db, category_id, owner_id=current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return update_category(db, category, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Удалить категорию."""
    category = get_category(db, category_id, owner_id=current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    delete_category(db, category)
