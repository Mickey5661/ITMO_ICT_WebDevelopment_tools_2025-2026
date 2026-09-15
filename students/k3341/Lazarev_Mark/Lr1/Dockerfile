FROM python:3.13-slim

# -u: логи сразу в stdout (видно в docker logs), без .pyc в образе
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# psycopg2-binary приезжает готовым колесом, поэтому gcc и libpq-dev
# в образе не нужны — меньше размер и меньше поверхность атаки.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Контейнер работает не от root
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/', timeout=3)" || exit 1

# Миграции выполняет отдельный сервис `migrate` из docker-compose,
# поэтому здесь только запуск сервера.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
