"""src/apps/announcements/routers/promotion.py."""

import logging
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status, Depends
from src.apps.announcements.schemas.promotion import (
    PromotionResponse,
    PromotionUpdate,
    PromotionCreate,
)
from src.apps.announcements.services.promotion import PromotionService
from src.apps.users.models import User
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/announcements", tags=["Promotion"])


@router.post(
    "/{announcement_id}/promotion",
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
    "/promotion/{promotion_id}",
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
    "/promotion/{promotion_id}",
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
