"""src/routes/announcements.py."""

from typing import List
from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka, inject

from src.models import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import (
    AnnouncementResponse,
    AnnouncementCreate,
    AnnouncementUpdate,
)
from src.services.announcements import AnnouncementService

router = APIRouter(tags=["Announcements"])


@router.post("/announcements", response_model=AnnouncementResponse)
@inject
async def create_announcement(
    service: FromDishka[AnnouncementService],
    data: AnnouncementCreate,
    user: User = Depends(get_current_user),
):
    """Создать объявление."""
    return await service.create_announcement(user.id, data)


@router.get("/announcements", response_model=List[AnnouncementResponse])
@inject
async def get_announcements(
    service: FromDishka[AnnouncementService],
):
    """Получить список объявлений."""
    return await service.get_announcements()


@router.patch("/announcements/{announcement_id}", response_model=AnnouncementResponse)
@inject
async def update_announcement(
    service: FromDishka[AnnouncementService],
    announcement_id: int,
    data: AnnouncementUpdate,
    user: User = Depends(get_current_user),
):
    """Обновить объявление."""
    return await service.update_announcement(user, announcement_id, data)


@router.delete("/announcements/{announcement_id}")
@inject
async def delete_announcement_by_id(
    service: FromDishka[AnnouncementService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """Удалить объявление."""
    return await service.delete_announcement(user, announcement_id=announcement_id)
