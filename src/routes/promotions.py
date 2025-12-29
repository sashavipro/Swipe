"""src/routes/promotions.py."""

import logging

from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.common.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    AuthenticationFailedError,
)
from src.models import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import (
    PromotionResponse,
    PromotionCreate,
    PromotionUpdate,
)
from src.services.promotions import PromotionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Promotion"])


@router.post(
    "/announcements/{announcement_id}/promotion",
    response_model=PromotionResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        ResourceAlreadyExistsError,
    ),
)
@inject
async def create_promotion(
    service: FromDishka[PromotionService],
    announcement_id: int,
    data: PromotionCreate,
    user: User = Depends(get_current_user),
):
    """
    Add promotion.
    """
    logger.info("User %s promoting announcement %s", user.id, announcement_id)
    return await service.create_promotion(user, announcement_id, data)


@router.patch(
    "/promotions/{promotion_id}",
    response_model=PromotionResponse,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def update_promotion(
    service: FromDishka[PromotionService],
    promotion_id: int,
    data: PromotionUpdate,
    user: User = Depends(get_current_user),
):
    """Update promotion settings."""
    return await service.update_promotion(user, promotion_id, data)


@router.delete(
    "/promotions/{promotion_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_promotion(
    service: FromDishka[PromotionService],
    promotion_id: int,
    user: User = Depends(get_current_user),
):
    """Delete promotion."""
    return await service.delete_promotion(user, promotion_id)
