"""tests/conftest.py."""

import asyncio
import pytest_asyncio

pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.infrastructure",
    "tests.fixtures.app",
    "tests.fixtures.auth",
]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Create an event loop instance for the entire test session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
