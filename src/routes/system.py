"""src/routes/system.py."""

from fastapi import APIRouter
from src.config import settings

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса.
    """
    return {"status": "ok", "db_host": settings.DB_HOST, "service": "swipe-api"}
