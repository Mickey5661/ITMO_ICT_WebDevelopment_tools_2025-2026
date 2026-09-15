from fastapi import FastAPI
from app.routers import auth, users, categories, tags, tasks, time_entries
from app.routers import parser as parser_router

app = FastAPI(
    title="Time Manager API",
    description="Серверное приложение для управления задачами и временем. ЛР1.",
    version="1.0.0",
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(tasks.router)
app.include_router(time_entries.router)
app.include_router(parser_router.router)  


@app.get("/", tags=["Корень"])
def root() -> dict:
    """Приветственный эндпоинт."""
    return {"message": "Time Manager API работает. Документация: /docs"}
