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
    Требует токен (Auth).
    """
    return await service.create_announcement(user.id, data)
