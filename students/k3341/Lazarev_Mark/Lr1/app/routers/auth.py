from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.crud.user import get_user_by_username, get_user_by_email, create_user
from app.auth.utils import verify_password
from app.auth.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Регистрация нового пользователя."""
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email уже используется")
    return create_user(db, user_data)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Вход в систему — возвращает JWT access token."""
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)
