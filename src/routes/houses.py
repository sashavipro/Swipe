"""src/routes/houses.py."""

import logging
from typing import List
from fastapi import APIRouter, status, Depends
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.models.users import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import HouseCreate, HouseResponse
from src.services.houses import HouseService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["House"])


@router.post(
    "/houses",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(409, 422, 403),
)
@inject
async def create_house(
    service: FromDishka[HouseService],
    data: HouseCreate,
    user: User = Depends(get_current_user),  # Теперь требуем юзера
):
    """
    Создать структуру дома (Только для Developer/Moderator).
    - **403**: Недостаточно прав.
    - **409**: Если дом с таким именем уже есть.
    """
    return await service.create_house(user, data)


@router.get("/houses", response_model=List[HouseResponse])
@inject
async def get_houses(
    service: FromDishka[HouseService],
):
    """Получить список всех домов."""
    return await service.get_houses()
