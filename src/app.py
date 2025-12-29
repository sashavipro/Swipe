"""src/app.py."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy import text
from src.common.exceptions import setup_exception_handlers
from src.container import make_container
from src.database import async_engine


from src.routes.system import router as system_router
from src.routes.auth import router as auth_router
from src.routes.user_profile import router as profile_router
from src.routes.favorites import router as favorites_router
from src.routes.houses import router as houses_router
from src.routes.announcements import router as announcements_router
from src.routes.promotions import router as promotions_router
from src.routes.admin.users import router as admin_users_router
from src.routes.admin.bans import router as admin_bans_router
from src.routes.admin.complaints import router as admin_complaints_router
from src.routes.admin.moderation import router as admin_moderation_router
from src.routes.chessboard import router as chessboard_router
from src.routes.saved_searches import router as saved_searches_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

USERS_PREFIX = "/users"
REAL_ESTATE_PREFIX = "/real-estate"
ADMIN_PREFIX = "/admin"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Manages the application lifecycle (startup/shutdown).
    """
    logger.info("App is starting up...")

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        raise e
    yield
    logger.info("App is shutting down...")
    await async_engine.dispose()
    logger.info("Database connection closed.")


def create_app() -> FastAPI:
    """
    Application Factory (Builder).
    Assembles the FastAPI application, configures DI, Middleware, and Routers.
    """
    app = FastAPI(
        title="Swipe Real Estate API",
        version="1.0.0",
        description="Real estate service API with chats and subscriptions",
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
    setup_exception_handlers(app)

    app.include_router(system_router)
    app.include_router(auth_router, prefix="/auth")

    app.include_router(profile_router, prefix=USERS_PREFIX)
    app.include_router(favorites_router, prefix=USERS_PREFIX)
    app.include_router(saved_searches_router, prefix=USERS_PREFIX)

    app.include_router(houses_router, prefix=REAL_ESTATE_PREFIX)
    app.include_router(announcements_router, prefix=REAL_ESTATE_PREFIX)
    app.include_router(promotions_router, prefix=REAL_ESTATE_PREFIX)
    app.include_router(chessboard_router, prefix=REAL_ESTATE_PREFIX)

    app.include_router(admin_users_router, prefix=ADMIN_PREFIX)
    app.include_router(admin_bans_router, prefix=ADMIN_PREFIX)
    app.include_router(admin_complaints_router, prefix=ADMIN_PREFIX)
    app.include_router(admin_moderation_router, prefix=ADMIN_PREFIX)

    return app
