"""src/apps/announcements/repositories/promotion.py."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.apps.announcements.models import Promotion, Announcement
from src.apps.announcements.schemas.promotion import PromotionCreate
from src.core.exceptions import ResourceNotFoundError, ResourceAlreadyExistsError

logger = logging.getLogger(__name__)


class PromotionRepository:
    """
    Repository for working with promotions.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_promotion(
        self,
        announcement_id: int,
        data: PromotionCreate,
    ) -> Promotion:
        """
        Creates a promotion record.
        Note: Permission checks are performed in the Services layer.
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
            raise ResourceNotFoundError()

        if announcement.promotion:
            logger.warning(
                "Promotion already exists for announcement_id=%s", announcement_id
            )
            raise ResourceAlreadyExistsError()

        promotion_data = data.model_dump()
        promo = Promotion(announcement_id=announcement_id, **promotion_data)

        self.session.add(promo)
        await self.session.flush()

        logger.info("Promotion created successfully: id=%s", promo.id)
        return promo

    async def get_promotion_by_id(self, promotion_id: int) -> Promotion | None:
        """Searches for promotion by ID."""
        logger.debug("Fetching promotion_id=%s", promotion_id)

        stmt = (
            select(Promotion)
            .options(selectinload(Promotion.announcement))
            .where(Promotion.id == promotion_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_promotion(self, promotion: Promotion, data: dict) -> Promotion:
        """Updates promotion fields."""
        logger.info("Updating promotion_id=%s", promotion.id)

        for key, value in data.items():
            if hasattr(promotion, key):
                setattr(promotion, key, value)

        self.session.add(promotion)
        await self.session.flush()
        return promotion

    async def delete_promotion(self, promotion: Promotion) -> None:
        """Deletes a promotion record."""
        logger.info("Deleting promotion_id=%s", promotion.id)

        await self.session.delete(promotion)
        await self.session.flush()
