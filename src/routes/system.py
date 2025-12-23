"""src/routes/system.py."""

import logging
from fastapi import APIRouter
from src.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса.
    """
    logger.debug("Health check requested")
    return {"status": "ok", "db_host": settings.DB_HOST, "service": "swipe-api"}
