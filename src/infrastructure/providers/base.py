"""src/infrastructure/providers/base.py."""

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis import asyncio as aioredis

from src.config import settings
from src.database import async_engine, async_session_factory
from src.infrastructure.storage import ImageStorage


class InfraProvider(Provider):
    """
    Infrastructure layer provider.
    """

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        """Returns the global SQLAlchemy engine."""
        return async_engine

    @provide(scope=Scope.APP)
    def get_session_factory(
        self, _engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Returns the global session factory."""
        return async_session_factory

    @provide(scope=Scope.APP)
    def get_image_storage(self) -> ImageStorage:
        """Returns the image storage service."""
        return ImageStorage()

    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncIterable[aioredis.Redis]:
        """Creates a Redis connection pool."""
        redis = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        yield redis
        await redis.close()

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """Creates a DB session for the current request."""
        async with session_factory() as session:
            yield session
