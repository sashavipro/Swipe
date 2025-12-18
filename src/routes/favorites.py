"""src/routes/favorites.py."""

from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka, inject

from src.models.users import User
from src.schemas.real_estate import AnnouncementResponse
from src.routes.deps import get_current_user
from src.services.favorites import FavoriteService

router = APIRouter(tags=["Favorite"])


@router.get("/me/favorites", response_model=list[AnnouncementResponse])
@inject
async def get_favorites(
    service: FromDishka[FavoriteService],
    user: User = Depends(get_current_user),
):
    """Показать избранные объявления."""
    return await service.get_my_favorites(user.id)


@router.post("/me/favorites/{announcement_id}")
@inject
async def add_to_favorites(
    service: FromDishka[FavoriteService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """Добавить в избранное."""
    return await service.add_to_favorites(user.id, announcement_id)


@router.delete("/me/favorites/{announcement_id}")
@inject
async def remove_from_favorites(
    service: FromDishka[FavoriteService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """Удалить из избранного."""
    return await service.remove_from_favorites(user.id, announcement_id)
