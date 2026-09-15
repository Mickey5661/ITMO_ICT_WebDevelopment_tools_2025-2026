import os
import requests
import psycopg2
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки сервиса-парсера.

    database_url без значения по умолчанию: креды не зашиты в код,
    а приходят из переменной окружения DATABASE_URL (в Docker — из
    docker-compose) либо из локального .env (см. .env.example).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str


settings = Settings()
app = FastAPI(title="Parser Service", description="Сервис парсинга веб-страниц")

PARSER_USERNAME = "parser_bot"
PARSER_EMAIL = "parser@bot.local"




def get_db_connection():
    """Открыть соединение с PostgreSQL."""
    return psycopg2.connect(settings.database_url)


def get_or_create_parser_user(conn) -> int:
    """Получить или создать системного пользователя-парсера."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (PARSER_USERNAME,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        hashed = "$2b$12$KIX6v9MwwsrEJrR6ELDpSOQ5Q4HhcpK1W/sKgzXd1lZp6cZLJM9N."
        cur.execute(
            """INSERT INTO users (username, email, hashed_password, is_active, created_at)
               VALUES (%s, %s, %s, TRUE, NOW()) RETURNING id""",
            (PARSER_USERNAME, PARSER_EMAIL, hashed),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


def save_task_to_db(conn, user_id: int, title: str, url: str) -> int:
    """Сохранить результат парсинга как задачу в таблицу tasks."""
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO tasks
               (title, description, priority, status, owner_id, created_at, updated_at)
               VALUES (%s, %s, 'low', 'todo', %s, NOW(), NOW())
               RETURNING id""",
            (title[:200], f"Источник: {url}", user_id),
        )
        task_id = cur.fetchone()[0]
        conn.commit()
        return task_id




class ParseRequest(BaseModel):
    url: str


class ParseResponse(BaseModel):
    url: str
    title: str
    task_id: int
    message: str




@app.get("/health")
def health_check():
    """Проверка состояния сервиса."""
    return {"status": "ok", "service": "parser"}


@app.post("/parse", response_model=ParseResponse)
def parse_and_save(request: ParseRequest) -> ParseResponse:
    """
    Загрузить страницу по URL, извлечь заголовок и сохранить в БД.
    Вызывается из основного FastAPI-приложения или Celery-воркера.
    """
    url = request.url
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Ошибка загрузки URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title else "Без заголовка"

    try:
        conn = get_db_connection()
        user_id = get_or_create_parser_user(conn)
        task_id = save_task_to_db(conn, user_id, title, url)
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка записи в БД: {e}")

    return ParseResponse(
        url=url,
        title=title,
        task_id=task_id,
        message="Парсинг выполнен, данные сохранены в БД",
    )


@app.get("/")
def root():
    return {"message": "Parser Service. Документация: /docs"}
