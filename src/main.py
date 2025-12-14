import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka

from src.config import settings
from src.container import make_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting up...")
    yield
    print("App is shutting down...")


def create_app() -> FastAPI:
    """
    Функция-сборщик. Создает и настраивает экземпляр приложения.
    """

    app = FastAPI(
        title="Swipe Real Estate API",
        version="1.0.0",
        description="API сервиса недвижимости с чатами и подписками",
        lifespan=lifespan,
        # docs_url=None,  # скрыть Swagger на проде
        # redoc_url=None
    )

    # В продакшене allow_origins=["*"] нужно заменить на конкретный домен фронта
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    container = make_container()
    setup_dishka(container, app)

    # from src.routes import users, real_estate, auth
    # app.include_router(auth.router)
    # app.include_router(users.router)
    # app.include_router(real_estate.router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "db_host": settings.DB_HOST}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
