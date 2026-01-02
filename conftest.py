"""src/tests/fixtures/conftest.py."""

import asyncio
import pytest_asyncio

pytest_plugins = [
    "src.tests.fixtures.database",
    "src.tests.fixtures.infrastructure",
    "src.tests.fixtures.app",
    "src.tests.fixtures.auth",
]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Create an event loop instance for the entire test session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
