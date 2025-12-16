"""src/app.py."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy import text

from src.container import make_container
from src.database import async_engine
from src.routes.system import router as system_router
from src.routes.auth import router as auth_router
from src.routes.users import router as users_router
from src.routes.real_estate import router as real_estate_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Управляет жизненным циклом приложения (startup/shutdown).
    Проверяет соединение с БД при старте и закрывает его при остановке.
    """
    print("App is starting up...")

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection established successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise e
    yield
    print("App is shutting down...")
    await async_engine.dispose()
    print("Database connection closed.")


def create_app() -> FastAPI:
    """
    Application Factory (Builder).
    Собирает FastAPI приложение, настраивает DI, Middleware и Роутеры.
    """
    app = FastAPI(
        title="Swipe Real Estate API",
        version="1.0.0",
        description="API сервиса недвижимости с чатами и подписками",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    container = make_container()
    setup_dishka(container, app)

    app.include_router(system_router)
    app.include_router(auth_router, prefix="/auth")
    app.include_router(users_router, prefix="/users")
    app.include_router(real_estate_router, prefix="/real-estate")

    return app
