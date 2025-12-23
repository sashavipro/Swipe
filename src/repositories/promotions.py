"""src/repositories/promotions.py."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.exceptions import ResourceNotFoundError, ResourceAlreadyExistsError
from src.models.real_estate import Announcement, Promotion
from src.schemas.real_estate import PromotionCreate

logger = logging.getLogger(__name__)


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
    ) -> Promotion:
        """
        Создает запись о продвижении.
        Примечание: Проверка прав доступа выполняется в слое Services.
        """
        logger.info(
            "Attempting to create promotion for announcement_id=%s",
            announcement_id,
        )

        stmt = (
            select(Announcement)
            .options(selectinload(Announcement.promotion))
            .where(Announcement.id == announcement_id)
        )
        announcement = (await self.session.execute(stmt)).scalar_one_or_none()

        if not announcement:
            logger.warning(
                "Promotion creation failed: Announcement %s not found", announcement_id
            )
            raise ResourceNotFoundError(
                f"Announcement with id {announcement_id} not found"
            )

        if announcement.promotion:
            logger.warning(
                "Promotion already exists for announcement_id=%s", announcement_id
            )
            raise ResourceAlreadyExistsError(
                "Promotion already exists for this announcement"
            )

        promotion_data = data.model_dump()
        promo = Promotion(announcement_id=announcement_id, **promotion_data)

        self.session.add(promo)
        await self.session.flush()

        logger.info("Promotion created successfully: id=%s", promo.id)
        return promo

    async def get_promotion_by_id(self, promotion_id: int) -> Promotion | None:
        """Ищет продвижение по ID."""
        logger.debug("Fetching promotion_id=%s", promotion_id)

        stmt = (
            select(Promotion)
            .options(selectinload(Promotion.announcement))
            .where(Promotion.id == promotion_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_promotion(self, promotion: Promotion, data: dict) -> Promotion:
        """Обновляет поля продвижения."""
        logger.info("Updating promotion_id=%s", promotion.id)

        for key, value in data.items():
            if hasattr(promotion, key):
                setattr(promotion, key, value)

        self.session.add(promotion)
        await self.session.flush()
        return promotion

    async def delete_promotion(self, promotion: Promotion) -> None:
        """Удаляет запись о продвижении."""
        logger.info("Deleting promotion_id=%s", promotion.id)

        await self.session.delete(promotion)
        await self.session.flush()
