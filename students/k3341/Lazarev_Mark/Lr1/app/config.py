from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения.

    database_url и secret_key НЕ имеют значений по умолчанию: если их забыли
    задать, приложение падает на старте с понятной ошибкой, а не запускается
    втихую с дефолтным паролем/ключом. Значения берутся из переменных
    окружения (в Docker) или из файла .env (при локальном запуске).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    secret_key: str

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    parser_url: str = "http://localhost:8001"


settings = Settings()
