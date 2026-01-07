"""tests/fixtures/app.py."""

from unittest.mock import MagicMock
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from dishka import make_async_container
from src.app import create_app
from src.infrastructure.tasks.email import send_email_task
from src.apps.auth.provider import AuthProvider
from src.apps.users.provider import UsersProvider
from src.apps.buildings.provider import BuildingsProvider
from src.apps.announcements.provider import AnnouncementsProvider
from src.apps.admin.provider import AdminProvider
from tests.fixtures.infrastructure import TestInfraProvider


@pytest_asyncio.fixture
async def app():
    """
    Creates a FastAPI application instance with a substituted DI container.
    """
    send_email_task.delay = MagicMock()

    container = make_async_container(
        TestInfraProvider(),
        AuthProvider(),
        UsersProvider(),
        BuildingsProvider(),
        AnnouncementsProvider(),
        AdminProvider(),
    )

    fastapi_app = create_app(container)
    fastapi_app.state.dishka_container = container

    yield fastapi_app
    await container.close()


@pytest_asyncio.fixture
async def client(app):  # pylint: disable=redefined-outer-name
    """
    Creates an asynchronous HTTP client for the application.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
