"""src/apps/users/routers/favorites.py."""

import logging

from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.apps.announcements.schemas.announcement import AnnouncementResponse
from src.apps.users.models import User
from src.apps.users.services.favorite import FavoriteService
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Favorite"])


@router.get(
    "/me/favorites",
    response_model=list[AnnouncementResponse],
    responses=create_error_responses(AuthenticationFailedError),
)
@inject
async def get_favorites(
    service: FromDishka[FavoriteService],
    user: User = Depends(get_current_user),
):
    """Show favorite announcements."""
    return await service.get_my_favorites(user.id)


@router.post(
    "/me/favorites/{announcement_id}",
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, ResourceNotFoundError, ResourceAlreadyExistsError
    ),
)
@inject
async def add_to_favorites(
    service: FromDishka[FavoriteService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """
    Add to favorites.
    """
    logger.info("User %s adding announcement %s to favorites", user.id, announcement_id)
    return await service.add_to_favorites(user.id, announcement_id)


@router.delete(
    "/me/favorites/{announcement_id}",
    responses=create_error_responses(AuthenticationFailedError),
)
@inject
async def remove_from_favorites(
    service: FromDishka[FavoriteService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """Remove from favorites."""
    logger.info(
        "User %s removing announcement %s from favorites", user.id, announcement_id
    )
    return await service.remove_from_favorites(user.id, announcement_id)
