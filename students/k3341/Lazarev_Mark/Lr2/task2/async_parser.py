import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import aiohttp
from bs4 import BeautifulSoup
from database import get_connection, ensure_parser_user, save_parsed_result

URLS = [
    "https://python.org",
    "https://fastapi.tiangolo.com",
    "https://docs.python.org/3/",
    "https://pypi.org",
    "https://realpython.com",
    "https://habr.com",
    "https://github.com",
    "https://stackoverflow.com",
]


def _save_to_db(title: str, url: str) -> None:
    """Синхронная запись в БД (psycopg2). Вызывается через executor."""
    conn = get_connection()
    user_id = ensure_parser_user(conn)
    save_parsed_result(conn, user_id, title, url)
    conn.close()


async def parse_and_save(
    session: aiohttp.ClientSession,
    url: str,
    executor: ThreadPoolExecutor,
) -> dict:
    """
    Асинхронно загрузить страницу, извлечь заголовок,
    сохранить в БД через executor (чтобы не блокировать event loop).
    """
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "Без заголовка"

        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, _save_to_db, title, url)

        print(f"  [OK] {url} → «{title}»")
        return {"url": url, "title": title, "status": "ok"}

    except Exception as e:
        print(f"  [ERR] {url} → {e}")
        return {"url": url, "title": None, "status": f"error: {e}"}


async def main_async() -> float:
    headers = {
        "User-Agent": "Mozilla/5.0",
        # Просим сервер не использовать brotli/zstd — aiohttp не всегда умеет их распаковать.
        # Так гарантированно получаем gzip/deflate, которые aiohttp декодирует из коробки.
        "Accept-Encoding": "gzip, deflate",
    }
    print(f"[Async / aiohttp] Парсинг {len(URLS)} URL")
    t0 = time.perf_counter()

    with ThreadPoolExecutor(max_workers=4) as db_executor:
        async with aiohttp.ClientSession(headers=headers) as session:
            
            
            tasks = [parse_and_save(session, url, db_executor) for url in URLS]
            results = await asyncio.gather(*tasks, return_exceptions=False)

    elapsed = time.perf_counter() - t0
    ok = sum(1 for r in results if isinstance(r, dict) and r["status"] == "ok")
    print(f"\n  Успешно: {ok}/{len(URLS)}, Время: {elapsed:.4f} сек\n")
    return elapsed


def main() -> float:
    return asyncio.run(main_async())


if __name__ == "__main__":
    main()
