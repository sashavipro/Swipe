"""src/repositories/promotions.py."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.real_estate import Announcement, Promotion
from src.schemas.real_estate import PromotionCreate


class PromotionRepository:
    """
    Репозиторий для работы с продвижениями.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_promotion(
        self,
        announcement_id: int,
        data: PromotionCreate,
        user_id: int | None = None,
    ) -> Promotion:
        """Создает запись о продвижении."""
        stmt = (
            select(Announcement)
            .options(selectinload(Announcement.promotion))
            .where(Announcement.id == announcement_id)
        )
        announcement = (await self.session.execute(stmt)).scalar_one_or_none()

        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        if user_id is not None and announcement.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to add promotion to this announcement",
            )

        if announcement.promotion:
            raise HTTPException(
                status_code=400, detail="Promotion already exists for this announcement"
            )

        promotion_data = data.model_dump()
        promo = Promotion(announcement_id=announcement_id, **promotion_data)

        self.session.add(promo)
        await self.session.flush()
        return promo

    async def get_promotion_by_id(self, promotion_id: int) -> Promotion | None:
        """Ищет продвижение по ID."""
        stmt = (
            select(Promotion)
            .options(selectinload(Promotion.announcement))
            .where(Promotion.id == promotion_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_promotion(self, promotion: Promotion, data: dict) -> Promotion:
        """Обновляет поля продвижения."""
        for key, value in data.items():
            if hasattr(promotion, key):
                setattr(promotion, key, value)

        self.session.add(promotion)
        await self.session.flush()
        return promotion

    async def delete_promotion(self, promotion: Promotion) -> None:
        """Удаляет запись о продвижении."""
        await self.session.delete(promotion)
        await self.session.flush()
