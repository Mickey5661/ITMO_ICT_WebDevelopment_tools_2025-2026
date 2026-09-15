"""
Окружение Alembic.

Строка подключения к БД не хранится ни в alembic.ini, ни в коде:
она читается из переменной окружения DATABASE_URL через app.config.settings.
Движок создаётся напрямую через create_engine, а не через engine_from_config,
чтобы URL с паролем вообще не попадал в объект конфигурации Alembic
(и не ломался о символ '%' при интерполяции ConfigParser).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import settings
from app.database import Base
import app.models  # noqa: F401 — регистрирует все модели в Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Вернуть URL подключения из окружения, либо упасть с понятной ошибкой."""
    url = settings.database_url
    if not url:
        raise RuntimeError(
            "DATABASE_URL не задан. Задайте переменную окружения "
            "или создайте .env по образцу .env.example. "
            "В alembic.ini секреты не хранятся."
        )
    return url


def run_migrations_offline() -> None:
    """Генерация SQL-скрипта без подключения к БД."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Применение миграций с активным подключением к БД."""
    connectable = create_engine(get_url(), poolclass=pool.NullPool)
    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
