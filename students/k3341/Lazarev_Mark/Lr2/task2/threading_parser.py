import threading
import time
import requests
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

results: list[dict] = []
lock = threading.Lock()


def parse_and_save(url: str) -> None:
    """
    Загрузить страницу по URL, извлечь заголовок и сохранить в БД.
    Выполняется в отдельном потоке.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "Без заголовка"

        
        conn = get_connection()
        user_id = ensure_parser_user(conn)
        save_parsed_result(conn, user_id, title, url)
        conn.close()

        with lock:
            results.append({"url": url, "title": title, "status": "ok"})
        print(f"  [OK] {url} → «{title}»")

    except Exception as e:
        with lock:
            results.append({"url": url, "title": None, "status": f"error: {e}"})
        print(f"  [ERR] {url} → {e}")


def main() -> float:
    threads = [threading.Thread(target=parse_and_save, args=(url,)) for url in URLS]

    print(f"[Threading] Парсинг {len(URLS)} URL в {len(URLS)} потоках")
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - t0

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n  Успешно: {ok}/{len(URLS)}, Время: {elapsed:.4f} сек\n")
    return elapsed


if __name__ == "__main__":
    main()
