"""src/app.py."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from dishka import AsyncContainer
from src.core.docs import VALIDATION_ERROR_RESPONSE
from src.core.exceptions import setup_exception_handlers
from src.core.lifecycle import lifespan
from src.apps.auth.router import router as auth_router
from src.apps.users.routers.user_profile import router as user_profile_router
from src.apps.users.routers.favorite import router as favorite_router
from src.apps.users.routers.saved_searches import router as saved_searches_router
from src.apps.users.routers.complaint import router as complaint_router
from src.apps.users.routers.chat import router as chat_router
from src.apps.buildings.routers import router as buildings_router
from src.apps.announcements.routers.announcement import router as ann_router
from src.apps.announcements.routers.chessboard import router as chessboard_router
from src.apps.announcements.routers.promotion import router as promotion_router
from src.apps.admin.routers.crud_user import router as admin_crud_router
from src.apps.admin.routers.blacklist import router as admin_blacklist_router
from src.apps.admin.routers.moderation_announcement import (
    router as admin_moderation_router,
)
from src.apps.admin.routers.system import router as admin_system_router


def create_app(container: AsyncContainer) -> FastAPI:
    """
    Application Factory.
    """
    app = FastAPI(
        title="Swipe Real Estate API",
        version="1.1.0",
        description="Modular API for Real Estate Swipe Application",
        lifespan=lifespan,
        responses={422: VALIDATION_ERROR_RESPONSE},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_dishka(container, app)
    setup_exception_handlers(app)

    app.include_router(auth_router)

    app.include_router(user_profile_router)
    app.include_router(favorite_router)
    app.include_router(saved_searches_router)
    app.include_router(complaint_router)
    app.include_router(chat_router)

    app.include_router(buildings_router)

    app.include_router(ann_router)
    app.include_router(chessboard_router)
    app.include_router(promotion_router)

    app.include_router(admin_crud_router)
    app.include_router(admin_blacklist_router)
    app.include_router(admin_moderation_router)
    app.include_router(admin_system_router)

    return app
