"""src/routes/favorites.py."""

import logging

from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.models.users import User
from src.schemas.real_estate import AnnouncementResponse
from src.routes.deps import get_current_user
from src.services.favorites import FavoriteService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Favorite"])


@router.get(
    "/me/favorites",
    response_model=list[AnnouncementResponse],
    responses=create_error_responses(401),
)
@inject
async def get_favorites(
    service: FromDishka[FavoriteService],
    user: User = Depends(get_current_user),
):
    """Показать избранные объявления."""
    return await service.get_my_favorites(user.id)


@router.post(
    "/me/favorites/{announcement_id}",
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(401, 404, 409, 422),
)
@inject
async def add_to_favorites(
    service: FromDishka[FavoriteService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """
    Добавить в избранное.
    - **409**: Уже в избранном.
    - **404**: Объявление не найдено.
    """
    logger.info("User %s adding announcement %s to favorites", user.id, announcement_id)
    return await service.add_to_favorites(user.id, announcement_id)


@router.delete(
    "/me/favorites/{announcement_id}", responses=create_error_responses(401, 422)
)
@inject
async def remove_from_favorites(
    service: FromDishka[FavoriteService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """Удалить из избранного."""
    logger.info(
        "User %s removing announcement %s from favorites", user.id, announcement_id
    )
    return await service.remove_from_favorites(user.id, announcement_id)
