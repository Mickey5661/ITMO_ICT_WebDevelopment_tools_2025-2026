"""
Celery-задачи для асинхронного парсинга.
Воркер получает задачу из очереди Redis и вызывает сервис парсера по HTTP.
"""

import httpx
from app.celery_app import celery_app
from app.config import settings


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def parse_url_task(self, url: str) -> dict:
    """
    Асинхронная Celery-задача: отправляет URL в сервис парсера.
    bind=True — позволяет обращаться к self для retry.
    max_retries=3 — повторяет задачу при ошибке до 3 раз.
    """
    try:
        
        response = httpx.post(
            f"{settings.parser_url}/parse",
            json={"url": url},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        
        raise self.retry(exc=exc)
