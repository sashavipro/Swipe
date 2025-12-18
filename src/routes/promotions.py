"""src/routes/promotions.py."""

from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka, inject

from src.models import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import (
    PromotionResponse,
    PromotionCreate,
    PromotionUpdate,
)
from src.services.promotions import PromotionService

router = APIRouter(tags=["Promotion"])


@router.post(
    "/announcements/{announcement_id}/promotion", response_model=PromotionResponse
)
@inject
async def create_promotion(
    service: FromDishka[PromotionService],
    announcement_id: int,
    data: PromotionCreate,
    user: User = Depends(get_current_user),
):
    """Добавить продвижение."""
    return await service.create_promotion(user, announcement_id, data)


@router.patch("/promotions/{promotion_id}", response_model=PromotionResponse)
@inject
async def update_promotion(
    service: FromDishka[PromotionService],
    promotion_id: int,
    data: PromotionUpdate,
    user: User = Depends(get_current_user),
):
    """Обновить настройки продвижения."""
    return await service.update_promotion(user, promotion_id, data)


@router.delete("/promotions/{promotion_id}")
@inject
async def delete_promotion(
    service: FromDishka[PromotionService],
    promotion_id: int,
    user: User = Depends(get_current_user),
):
    """Удалить продвижение."""
    return await service.delete_promotion(user, promotion_id)
