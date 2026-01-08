"""src/lifecycle.py."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from src.infrastructure.database.setup import async_engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application lifecycle management.
    """
    logger.info("Starting up: Checking infrastructure...")
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection: OK")
    except Exception as e:
        logger.error("Database connection: FAILED. Error: %s", e)
        raise e

    yield

    logger.info("Shutting down: Cleaning up resources...")
    await async_engine.dispose()
    logger.info("Resources cleaned up.")
