"""src/services/promotions.py."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import ResourceNotFoundError
from src.common.utils import check_owner_or_admin
from src.models import User
from src.repositories.promotions import PromotionRepository
from src.repositories.announcements import AnnouncementRepository
from src.schemas.real_estate import (
    PromotionCreate,
    PromotionResponse,
    PromotionUpdate,
)

logger = logging.getLogger(__name__)


class PromotionService:
    """
    Сервис для работы с продвижениями.
    """

    def __init__(
        self,
        repo: PromotionRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.announcement_repo = announcement_repo
        self.session = session

    async def create_promotion(
        self, user: User, announcement_id: int, data: PromotionCreate
    ) -> PromotionResponse:
        """Создать продвижение для объявления."""
        logger.info(
            "User %s creating promotion for announcement %s", user.id, announcement_id
        )

        announcement = await self.announcement_repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError(
                f"Announcement with id {announcement_id} not found"
            )

        check_owner_or_admin(
            user,
            announcement.user_id,
            "You do not have permission to add promotion to this announcement",
        )

        promo = await self.repo.create_promotion(announcement_id, data)
        await self.session.commit()

        logger.info("Promotion created successfully: id=%s", promo.id)
        return promo

    async def update_promotion(
        self, user: User, promotion_id: int, data: PromotionUpdate
    ) -> PromotionResponse:
        """
        Обновляет настройки продвижения.
        """
        promotion = await self.repo.get_promotion_by_id(promotion_id)
        if not promotion:
            logger.warning("Update failed: Promotion %s not found", promotion_id)
            raise ResourceNotFoundError(f"Promotion with id {promotion_id} not found")

        check_owner_or_admin(
            user,
            promotion.announcement.user_id,
            "You do not have permission to update this promotion",
        )

        update_data = data.model_dump(exclude_unset=True)
        updated_promo = await self.repo.update_promotion(promotion, update_data)
        await self.session.commit()

        logger.info("Promotion %s updated by user %s", promotion_id, user.id)
        return updated_promo

    async def delete_promotion(self, user: User, promotion_id: int):
        """
        Удаляет продвижение.
        """
        promotion = await self.repo.get_promotion_by_id(promotion_id)
        if not promotion:
            logger.warning("Delete failed: Promotion %s not found", promotion_id)
            raise ResourceNotFoundError(f"Promotion with id {promotion_id} not found")

        check_owner_or_admin(
            user,
            promotion.announcement.user_id,
            "You do not have permission to delete this promotion",
        )

        await self.repo.delete_promotion(promotion)
        await self.session.commit()

        logger.info("Promotion %s deleted by user %s", promotion_id, user.id)
        return {"status": "deleted", "id": promotion_id}
