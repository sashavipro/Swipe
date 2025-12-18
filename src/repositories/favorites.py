"""src/repositories/favorites.py."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.users import Chosen
from src.models.real_estate import Announcement


class FavoriteRepository:
    """
    Репозиторий для работы с избранным.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_favorite(self, user_id: int, announcement_id: int) -> None:
        """Добавляет объявление в избранное."""
        chosen = Chosen(user_id=user_id, announcement_id=announcement_id)
        self.session.add(chosen)
        await self.session.flush()

    async def remove_favorite(self, user_id: int, announcement_id: int) -> None:
        """Удаляет объявление из избранного."""
        stmt = select(Chosen).where(
            Chosen.user_id == user_id, Chosen.announcement_id == announcement_id
        )
        result = await self.session.execute(stmt)
        chosen = result.scalar_one_or_none()

        if chosen:
            await self.session.delete(chosen)
            await self.session.flush()

    async def get_favorite_status(self, user_id: int, announcement_id: int) -> bool:
        """Проверяет, находится ли объявление в избранном."""
        stmt = select(Chosen).where(
            Chosen.user_id == user_id, Chosen.announcement_id == announcement_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_favorites(self, user_id: int) -> list[Announcement]:
        """Возвращает список избранного."""
        query = (
            select(Announcement)
            .join(Chosen, Chosen.announcement_id == Announcement.id)
            .where(Chosen.user_id == user_id)
            .options(
                selectinload(Announcement.images), selectinload(Announcement.promotion)
            )
            .order_by(Chosen.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()
