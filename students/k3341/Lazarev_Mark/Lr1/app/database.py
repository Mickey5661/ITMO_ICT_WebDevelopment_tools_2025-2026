from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


engine = create_engine(settings.database_url)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""
    pass


def get_db():
    """
    Dependency-функция для FastAPI.
    Открывает сессию БД на время запроса и закрывает после.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
