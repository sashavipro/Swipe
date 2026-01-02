"""src/tests/fixtures/infrastructure.py."""

from typing import AsyncGenerator
from unittest.mock import MagicMock, AsyncMock

import fakeredis.aioredis
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import Provider, Scope, provide

from src.infrastructure.storage import ImageStorage
from src.tests.fixtures.database import test_session_factory


class TestInfraProvider(Provider):
    """
    Infrastructure provider for tests.
    Replaces real Redis, Cloudinary, and database sessions.
    """

    scope = Scope.APP

    @provide(scope=Scope.APP)
    def get_image_storage(self) -> ImageStorage:
        """Returns a mocked ImageStorage (Cloudinary)."""
        mock_storage = MagicMock(spec=ImageStorage)
        mock_storage.upload_file = AsyncMock(
            return_value="https://res.cloudinary.com/demo/image/upload/sample.jpg"
        )
        mock_storage.delete_file = AsyncMock(return_value=None)
        return mock_storage

    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncGenerator[aioredis.Redis, None]:
        """Returns a FakeRedis client (in-memory)."""
        redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        yield redis
        await redis.aclose()

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Session for the application.
        """
        async with test_session_factory() as session:
            yield session
