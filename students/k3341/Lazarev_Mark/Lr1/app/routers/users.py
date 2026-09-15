from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate, PasswordChange
from app.crud.user import get_users, get_user, update_user, delete_user
from app.auth.jwt import get_current_user
from app.auth.utils import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Получить информацию о текущем пользователе."""
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[UserRead]:
    """Получить список всех пользователей."""
    return get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> UserRead:
    """Получить пользователя по ID."""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.patch("/me", response_model=UserRead)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """Обновить данные текущего пользователя."""
    return update_user(db, current_user, data)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Сменить пароль текущего пользователя."""
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Удалить аккаунт текущего пользователя."""
    delete_user(db, current_user)
