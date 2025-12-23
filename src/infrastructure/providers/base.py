"""src/infrastructure/providers/base.py."""

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis import asyncio as aioredis  # pip install redis

from src.config import settings
from src.database import async_engine, async_session_factory
from src.infrastructure.storage import ImageStorage


class InfraProvider(Provider):
    """
    Провайдер инфраструктурного уровня.
    """

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        """Возвращает глобальный движок SQLAlchemy."""
        return async_engine

    @provide(scope=Scope.APP)
    def get_session_factory(
        self, _engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Возвращает глобальную фабрику сессий."""
        return async_session_factory

    @provide(scope=Scope.APP)
    def get_image_storage(self) -> ImageStorage:
        """Возвращает сервис для работы с хранилищем изображений."""
        return ImageStorage()

    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncIterable[aioredis.Redis]:
        """Создает пул соединений с Redis."""
        redis = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        yield redis
        await redis.close()

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """Создает сессию БД для текущего запроса."""
        async with session_factory() as session:
            yield session
