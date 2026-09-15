# Time Manager API — ЛР1

Автор: Лазарев Марк, ИСУ 368418

FastAPI-приложение для управления задачами и временем.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM
- **PostgreSQL** — база данных
- **Alembic** — миграции
- **JWT (jose)** — аутентификация
- **bcrypt** — хэширование паролей (вызывается напрямую, без обёрток)

## Конфигурация

Секреты не хранятся ни в коде, ни в `alembic.ini`. Настройки читаются из
переменных окружения, а при локальном запуске — из файла `.env`
(в git не попадает, образец — `.env.example`):

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `DATABASE_URL` | да | строка подключения к PostgreSQL (её же использует Alembic) |
| `SECRET_KEY` | да | ключ подписи JWT |
| `ALGORITHM` | нет | алгоритм JWT, по умолчанию `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | нет | время жизни токена, по умолчанию 30 |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | нет | Redis для очереди задач |
| `PARSER_URL` | нет | адрес сервиса-парсера (ЛР3) |

Если `DATABASE_URL` или `SECRET_KEY` не заданы, приложение падает на старте
с понятной ошибкой — вместо тихого запуска с дефолтным паролем.

## Установка и запуск

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать .env
cp .env.example .env
# заполнить DATABASE_URL и SECRET_KEY
# новый ключ: python -c "import secrets; print(secrets.token_urlsafe(48))"

# 3. Применить миграции
alembic upgrade head

# 4. Запустить сервер
uvicorn app.main:app --reload
```

Документация API: http://localhost:8000/docs

В Docker миграции применяет отдельный сервис `migrate` из `docker-compose.yml` третьей лабы,
поэтому `CMD` в Dockerfile только поднимает uvicorn.

## Структура проекта

```
app/
├── main.py          — точка входа
├── config.py        — конфигурация (переменные окружения / .env)
├── database.py      — подключение к БД
├── models/          — SQLAlchemy модели
├── schemas/         — Pydantic схемы
├── crud/            — CRUD операции
├── routers/         — API эндпоинты
└── auth/            — JWT и хэширование
alembic/             — миграции (URL берётся из DATABASE_URL, не из alembic.ini)
```

## Модели данных

| Таблица       | Описание                              |
|---------------|---------------------------------------|
| users         | Пользователи системы                  |
| categories    | Категории задач (one-to-many с tasks) |
| tags          | Теги (many-to-many с tasks)           |
| tasks         | Задачи с приоритетом и дедлайном      |
| task_tags     | Связь задача↔тег с полем note         |
| time_entries  | Записи затраченного времени           |
