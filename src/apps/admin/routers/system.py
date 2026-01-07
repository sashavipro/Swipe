"""src/apps/admin/routers/system.py."""

import logging
from fastapi import APIRouter
from src.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["System"])


@router.get("/health")
async def health_check():
    """
    Check service health.
    """
    logger.debug("Health check requested")
    return {"status": "ok", "db_host": settings.DB_HOST, "service": "swipe-api"}
