from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator


def _naive(dt: datetime | None) -> datetime | None:
    """
    Привести дату к «наивному» виду (без часового пояса).

    Swagger присылает время с суффиксом Z, а в базе колонка объявлена как
    DateTime без пояса. Если не привести оба значения к одному виду,
    вычитание одной даты из другой падает с TypeError.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def check_time_consistency(
    started_at: datetime | None,
    ended_at: datetime | None,
    duration_minutes: int | None,
) -> None:
    """
    Проверить, что запись времени осмысленна.

    Правила:
      1. Конец не может быть раньше начала.
      2. Потраченное время не может превышать интервал между началом и концом.
         Обратное допустимо: работал с 10:00 до 12:00, но полчаса пил кофе —
         тогда интервал 120 минут, а duration_minutes 90.

    Если ended_at не задан (запись ещё «идёт»), проверять нечего.
    Бросает ValueError — Pydantic превращает его в 422, роутер в 400.
    """
    started_at = _naive(started_at)
    ended_at = _naive(ended_at)

    if started_at is None or ended_at is None:
        return

    if ended_at <= started_at:
        raise ValueError("ended_at должен быть позже started_at")

    if duration_minutes is not None:
        interval_minutes = (ended_at - started_at).total_seconds() / 60
        # допуск в одну минуту — на округление секунд
        if duration_minutes > interval_minutes + 1:
            raise ValueError(
                f"duration_minutes ({duration_minutes}) больше интервала между "
                f"started_at и ended_at ({interval_minutes:.0f} мин)"
            )


class TimeEntryCreate(BaseModel):
    duration_minutes: int = Field(..., gt=0)
    started_at: datetime
    ended_at: datetime | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> "TimeEntryCreate":
        check_time_consistency(self.started_at, self.ended_at, self.duration_minutes)
        return self


class TimeEntryRead(BaseModel):
    id: int
    task_id: int
    duration_minutes: int
    started_at: datetime
    ended_at: datetime | None
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TimeEntryUpdate(BaseModel):
    duration_minutes: int | None = Field(None, gt=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> "TimeEntryUpdate":
        # Здесь видно только то, что прислали. Полную проверку с учётом
        # уже сохранённых значений делает роутер.
        check_time_consistency(self.started_at, self.ended_at, self.duration_minutes)
        return self
