"""
Роутер для вызова парсер-сервиса из основного FastAPI-приложения.

Подзадача 2: синхронный вызов — POST /parser/parse
    Клиент → API → parser-сервис → результат → клиент

Подзадача 3: асинхронный вызов через Celery — POST /parser/parse/async
    Клиент → API → Redis-очередь (задача) → Celery-воркер → parser-сервис
    Клиент сразу получает task_id и может проверять статус через GET /parser/task/{task_id}
"""

import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.config import settings
from app.tasks import parse_url_task
from app.models.user import User
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/parser", tags=["Парсер"])


class ParseRequest(BaseModel):
    url: str


class AsyncParseResponse(BaseModel):
    task_id: str
    status: str
    message: str




@router.post("/parse")
def parse_sync(
    request: ParseRequest,
    _: User = Depends(get_current_user),
) -> dict:
    """
    Синхронный вызов парсера.
    API проксирует запрос к parser-сервису и возвращает результат клиенту.
    Клиент ждёт пока парсинг завершится.
    """
    try:
        response = httpx.post(
            f"{settings.parser_url}/parse",
            json={"url": request.url},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Сервис парсера недоступен")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Таймаут запроса к парсеру")




@router.post("/parse/async", response_model=AsyncParseResponse)
def parse_async(
    request: ParseRequest,
    _: User = Depends(get_current_user),
) -> AsyncParseResponse:
    """
    Асинхронный вызов парсера через Celery.
    Задача помещается в Redis-очередь, Celery-воркер обработает её в фоне.
    Клиент немедленно получает task_id и не ждёт результата.
    """
    task = parse_url_task.delay(request.url)
    return AsyncParseResponse(
        task_id=task.id,
        status="queued",
        message=f"Задача поставлена в очередь. Проверьте статус: GET /parser/task/{task.id}",
    )


@router.get("/task/{task_id}")
def get_task_status(
    task_id: str,
    _: User = Depends(get_current_user),
) -> dict:
    """
    Проверить статус и результат Celery-задачи по её ID.
    Статусы: PENDING → STARTED → SUCCESS / FAILURE
    """
    task_result = parse_url_task.AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    if task_result.successful():
        response["result"] = task_result.result
    elif task_result.failed():
        response["error"] = str(task_result.result)
    return response
