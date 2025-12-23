"""src/routes/houses.py."""

import logging
from typing import List
from fastapi import APIRouter, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.schemas.real_estate import HouseCreate, HouseResponse
from src.services.houses import HouseService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["House"])


@router.post(
    "/houses",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(409, 422),
)
@inject
async def create_house(
    service: FromDishka[HouseService],
    data: HouseCreate,
):
    """
    Создать структуру дома.
    - **409**: Если дом с таким именем уже есть.
    """
    logger.info("Creating new house structure: %s", data.name)
    return await service.create_house(data)


@router.get("/houses", response_model=List[HouseResponse])
@inject
async def get_houses(
    service: FromDishka[HouseService],
):
    """Получить список всех домов."""
    return await service.get_houses()
