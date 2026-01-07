"""src/infrastructure/provider.py."""

from typing import AsyncIterable
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis.asyncio import Redis, from_url
from src.core.config import settings
from src.infrastructure.database.setup import async_engine, async_session_factory
from src.infrastructure.storage import ImageStorage


class InfraProvider(Provider):
    """
    Infrastructure layer provider.
    """

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        """
        Provides the global SQLAlchemy asynchronous engine.
        """
        return async_engine

    @provide(scope=Scope.APP)
    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        Provides the global session factory.
        """
        return async_session_factory

    @provide(scope=Scope.APP)
    def get_storage(self) -> ImageStorage:
        """
        Provides the ImageStorage service.
        """
        return ImageStorage()

    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncIterable[Redis]:
        """
        Creates and manages the Redis connection pool.
        """
        redis = from_url(settings.REDIS_URL, decode_responses=True)
        yield redis
        await redis.close()

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """
        Creates a new database session for the current request context.
        """
        async with factory() as session:
            yield session
