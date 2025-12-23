"""src/routes/announcements.py."""

import logging
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, Query
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.models import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import (
    AnnouncementResponse,
    AnnouncementCreate,
    AnnouncementUpdate,
)
from src.services.announcements import AnnouncementService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Announcements"])


@router.post(
    "/announcements",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(401, 422),
)
@inject
async def create_announcement(
    service: FromDishka[AnnouncementService],
    data: AnnouncementCreate,
    user: User = Depends(get_current_user),
):
    """
    Создать объявление.
    """
    logger.info("User %s creating announcement", user.id)
    return await service.create_announcement(user.id, data)


@router.get("/announcements", response_model=List[AnnouncementResponse])
@inject
async def get_announcements(
    service: FromDishka[AnnouncementService],
    limit: Annotated[
        int, Query(ge=1, le=100, description="Количество записей (макс 100)")
    ] = 20,
    offset: Annotated[int, Query(ge=0, description="Смещение")] = 0,
):
    """
    Получить список объявлений с пагинацией.
    """
    return await service.get_announcements(limit=limit, offset=offset)


@router.patch(
    "/announcements/{announcement_id}",
    response_model=AnnouncementResponse,
    responses=create_error_responses(401, 403, 404, 422),
)
@inject
async def update_announcement(
    service: FromDishka[AnnouncementService],
    announcement_id: int,
    data: AnnouncementUpdate,
    user: User = Depends(get_current_user),
):
    """
    Обновить объявление.
    """
    logger.info("User %s updating announcement %s", user.id, announcement_id)
    return await service.update_announcement(user, announcement_id, data)


@router.delete(
    "/announcements/{announcement_id}",
    responses=create_error_responses(401, 403, 404, 422),
)
@inject
async def delete_announcement_by_id(
    service: FromDishka[AnnouncementService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """
    Удалить объявление.
    """
    logger.info("User %s deleting announcement %s", user.id, announcement_id)
    return await service.delete_announcement(user, announcement_id=announcement_id)
