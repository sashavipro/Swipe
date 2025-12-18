"""src/routes/real_estate.py."""

from typing import List
from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka, inject

from src.models import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import (
    HouseCreate,
    HouseResponse,
    AnnouncementResponse,
    AnnouncementCreate,
    PromotionResponse,
    PromotionCreate,
    PromotionUpdate,
    AnnouncementUpdate,
)
from src.services.real_estate import RealEstateService

router = APIRouter(tags=["Real Estate"])


@router.post("/houses", response_model=HouseResponse)
@inject
async def create_house(
    service: FromDishka[RealEstateService],
    data: HouseCreate,
):
    """
    Создать структуру дома.
    """
    return await service.create_house(data)


@router.get("/houses", response_model=List[HouseResponse])
@inject
async def get_houses(
    service: FromDishka[RealEstateService],
):
    """Получить список всех домов со структурой."""
    return await service.get_houses()


@router.post("/announcements", response_model=AnnouncementResponse)
@inject
async def create_announcement(
    service: FromDishka[RealEstateService],
    data: AnnouncementCreate,
    user: User = Depends(get_current_user),
):
    """
    Создать объявление о продаже квартиры.
    """

    return await service.create_announcement(user.id, data)


@router.post(
    "/announcements/{announcement_id}/promotion", response_model=PromotionResponse
)
@inject
async def create_promotion(
    service: FromDishka[RealEstateService],
    announcement_id: int,
    data: PromotionCreate,
    user: User = Depends(get_current_user),
):
    """Добавить продвижение к объявлению."""
    return await service.create_promotion(user, announcement_id, data)


@router.get("/announcements", response_model=List[AnnouncementResponse])
@inject
async def get_announcements(
    service: FromDishka[RealEstateService],
):
    """
    Получить список всех объявлений.
    Сортировка: сначала Turbo, потом новые.
    """
    return await service.get_announcements()


@router.delete("/announcements/{announcement_id}")
@inject
async def delete_announcement_by_id(
    service: FromDishka[RealEstateService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """
    Удалить объявление по его ID.
    Доступно только владельцу.
    """
    return await service.delete_announcement(user, announcement_id=announcement_id)


@router.delete("/promotions/{promotion_id}")
@inject
async def delete_promotion(
    service: FromDishka[RealEstateService],
    promotion_id: int,
    user: User = Depends(get_current_user),
):
    """
    Удалить продвижение по его ID.
    """
    return await service.delete_promotion(user, promotion_id)


@router.patch("/announcements/{announcement_id}", response_model=AnnouncementResponse)
@inject
async def update_announcement(
    service: FromDishka[RealEstateService],
    announcement_id: int,
    data: AnnouncementUpdate,
    user: User = Depends(get_current_user),
):
    """
    Обновить данные объявления.
    """
    return await service.update_announcement(user, announcement_id, data)


@router.patch("/promotions/{promotion_id}", response_model=PromotionResponse)
@inject
async def update_promotion(
    service: FromDishka[RealEstateService],
    promotion_id: int,
    data: PromotionUpdate,
    user: User = Depends(get_current_user),
):
    """
    Обновить настройки продвижения.
    """
    return await service.update_promotion(user, promotion_id, data)
