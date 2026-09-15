import os
import psycopg2
from psycopg2.extensions import connection as PgConnection
from dotenv import load_dotenv


# Папка первой лабы может называться по-разному (lab1 в рабочей копии, Lr1 в
# репозитории курса), поэтому ищем .env по обоим именам, а не по жёсткому пути.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
for _name in ("lab1", "Lr1", "lr1"):
    _candidate = os.path.join(_ROOT, _name, ".env")
    if os.path.isfile(_candidate):
        load_dotenv(_candidate)
        break

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL не задан. Скопируйте .env.example в .env в папке первой лабы "
        "и заполните строку подключения — креды в коде не хранятся."
    )

PARSER_USERNAME = "parser_bot"
PARSER_EMAIL = "parser@bot.local"


def get_connection() -> PgConnection:
    """Открыть новое соединение с PostgreSQL."""
    return psycopg2.connect(DATABASE_URL)


def ensure_parser_user(conn: PgConnection) -> int:
    """
    Убедиться, что пользователь-парсер существует в БД.
    Возвращает его id.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (PARSER_USERNAME,))
        row = cur.fetchone()
        if row:
            return row[0]

        
        hashed = "$2b$12$KIX6v9MwwsrEJrR6ELDpSOQ5Q4HhcpK1W/sKgzXd1lZp6cZLJM9N."
        cur.execute(
            """
            INSERT INTO users (username, email, hashed_password, is_active, created_at)
            VALUES (%s, %s, %s, TRUE, NOW())
            RETURNING id
            """,
            (PARSER_USERNAME, PARSER_EMAIL, hashed),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


def save_parsed_result(
    conn: PgConnection, user_id: int, title: str, url: str
) -> None:
    """
    Сохранить результат парсинга как задачу в таблице tasks.
    title — заголовок страницы, url — адрес источника в описании.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tasks
                (title, description, priority, status, owner_id, created_at, updated_at)
            VALUES (%s, %s, 'low', 'todo', %s, NOW(), NOW())
            """,
            (title[:200], f"Источник: {url}", user_id),
        )
        conn.commit()
