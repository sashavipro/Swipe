"""src/tests/fixtures/database.py."""

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.config import settings
from src.models import Base


TEST_DB_NAME = f"{settings.DB_NAME}_test"
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    f"/{settings.DB_NAME}", f"/{TEST_DB_NAME}"
)
SYS_DATABASE_URL = settings.DATABASE_URL.replace(f"/{settings.DB_NAME}", "/postgres")


test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
test_session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def ensure_test_database_exists():
    """
    Checks and creates a test database.
    """
    sys_engine = create_async_engine(SYS_DATABASE_URL, isolation_level="AUTOCOMMIT")
    try:
        async with sys_engine.connect() as conn:
            query = text(f"SELECT 1 FROM pg_database WHERE datname='{TEST_DB_NAME}'")
            result = await conn.execute(query)
            if not result.scalar():
                print(f"Creating test database: {TEST_DB_NAME}...")
                await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    finally:
        await sys_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database_schema(
    ensure_test_database_exists,  # pylint: disable=redefined-outer-name, unused-argument
):
    """
    We roll out the database schema once per session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(
    setup_database_schema,  # pylint: disable=redefined-outer-name, unused-argument
):
    """
    Clears data in tables after each test (TRUNCATE).
    """
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(
                text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE")
            )
