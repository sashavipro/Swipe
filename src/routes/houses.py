"""src/routes/houses.py."""

from typing import List
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from src.schemas.real_estate import HouseCreate, HouseResponse
from src.services.houses import HouseService

router = APIRouter(tags=["House"])


@router.post("/houses", response_model=HouseResponse)
@inject
async def create_house(
    service: FromDishka[HouseService],
    data: HouseCreate,
):
    """Создать структуру дома."""
    return await service.create_house(data)


@router.get("/houses", response_model=List[HouseResponse])
@inject
async def get_houses(
    service: FromDishka[HouseService],
):
    """Получить список всех домов."""
    return await service.get_houses()
