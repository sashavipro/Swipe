"""src/services/favorites.py."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.favorites import FavoriteRepository
from src.schemas.real_estate import AnnouncementResponse


class FavoriteService:
    """
    Сервис для работы с избранными.
    """

    def __init__(self, repo: FavoriteRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def add_to_favorites(self, user_id: int, announcement_id: int):
        """
        Добавления в избранное.
        """
        is_favorite = await self.repo.get_favorite_status(user_id, announcement_id)
        if is_favorite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Announcement is already in favorites",
            )
        try:
            await self.repo.add_favorite(user_id, announcement_id)
            await self.session.commit()
        except Exception as e:
            if "ForeignKeyViolation" in str(e) or "IntegrityError" in str(e):
                raise HTTPException(
                    status_code=404, detail="Announcement not found"
                ) from e
            raise
        return {"status": "added", "announcement_id": announcement_id}

    async def remove_from_favorites(self, user_id: int, announcement_id: int):
        """
        Удаления из избранного.
        """
        await self.repo.remove_favorite(user_id, announcement_id)
        await self.session.commit()
        return {"status": "removed", "announcement_id": announcement_id}

    async def get_my_favorites(self, user_id: int) -> list[AnnouncementResponse]:
        """
        Получения избранного.
        """
        return await self.repo.get_favorites(user_id)
