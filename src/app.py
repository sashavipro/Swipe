"""src/app.py."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy import text
from src.common.exceptions import setup_exception_handlers
from src.container import make_container
from src.database import async_engine, async_session_factory
from src.infrastructure.security.password import PasswordHandler
from src.models.users import UserRole
from src.repositories.users import UserRepository

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


from src.schemas.users import UserCreateBase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

USERS_PREFIX = "/users"
REAL_ESTATE_PREFIX = "/real-estate"
ADMIN_PREFIX = "/admin"


async def create_default_moderator():
    """
    Создает дефолтного модератора, если он не существует.
    """
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        email = "moderator@moderator.com"

        # Проверяем, есть ли уже такой пользователь
        if await user_repo.get_by_email(email):
            logger.info("Default moderator already exists.")
            return

        logger.info("Creating default moderator...")
        try:
            user_data = UserCreateBase(
                email=email,
                password="moderator",
                first_name="System",
                last_name="Moderator",
                phone="+80009998877",
            )

            hashed_password = PasswordHandler.get_password_hash("moderator")

            await user_repo.create_user(
                data=user_data, hashed_password=hashed_password, role=UserRole.MODERATOR
            )
            await session.commit()
            logger.info("Default moderator created successfully.")

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to create default moderator: %s", e)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Управляет жизненным циклом приложения (startup/shutdown).
    """
    logger.info("App is starting up...")

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        raise e

    await create_default_moderator()

    yield

    logger.info("App is shutting down...")
    await async_engine.dispose()
    logger.info("Database connection closed.")


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
    setup_exception_handlers(app)

    app.include_router(system_router)
    app.include_router(auth_router, prefix="/auth")

    app.include_router(profile_router, prefix=USERS_PREFIX)
    app.include_router(favorites_router, prefix=USERS_PREFIX)

    app.include_router(houses_router, prefix=REAL_ESTATE_PREFIX)
    app.include_router(announcements_router, prefix=REAL_ESTATE_PREFIX)
    app.include_router(promotions_router, prefix=REAL_ESTATE_PREFIX)
    app.include_router(admin_users_router, prefix=ADMIN_PREFIX)
    app.include_router(admin_bans_router, prefix=ADMIN_PREFIX)
    app.include_router(admin_complaints_router, prefix=ADMIN_PREFIX)
    app.include_router(admin_moderation_router, prefix=ADMIN_PREFIX)

    return app
