"""src/tests/fixtures/app.py."""

from unittest.mock import MagicMock, patch

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from dishka import make_async_container

from src.main import create_app
from src.infrastructure.providers.repositories import RepositoryProvider
from src.infrastructure.providers.services import ServiceProvider
from src.tasks.email import send_email_task
from src.tests.fixtures.infrastructure import TestInfraProvider


@pytest_asyncio.fixture
async def app():
    """
    FastAPI application fixture with a replaced DI container.
    """
    send_email_task.delay = MagicMock()

    container = make_async_container(
        TestInfraProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )

    if hasattr(container.registry, "scope_generators"):
        with list(container.registry.scope_generators.values())[0]:
            pass

    with patch("src.app.make_container", return_value=container):
        fastapi_app = create_app()
        fastapi_app.state.dishka_container = container
        yield fastapi_app

    await container.close()


@pytest_asyncio.fixture
async def client(app):  # pylint: disable=redefined-outer-name
    """
    Asynchronous HTTP client.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
