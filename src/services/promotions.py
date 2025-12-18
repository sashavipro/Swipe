"""src/services/promotions.py."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User
from src.models.users import UserRole
from src.repositories.promotions import PromotionRepository
from src.schemas.real_estate import (
    PromotionCreate,
    PromotionResponse,
    PromotionUpdate,
)


class PromotionService:
    """
    Сервис для работы с продвижениями.
    """

    def __init__(self, repo: PromotionRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_promotion(
        self, user: User, announcement_id: int, data: PromotionCreate
    ) -> PromotionResponse:
        """Создать продвижение для объявления."""
        check_user_id = user.id
        if user.role in [UserRole.MODERATOR, UserRole.AGENT]:
            check_user_id = None

        promo = await self.repo.create_promotion(announcement_id, data, check_user_id)
        await self.session.commit()
        return promo

    async def update_promotion(
        self, user: User, promotion_id: int, data: PromotionUpdate
    ) -> PromotionResponse:
        """
        Обновляет объявление.
        """
        promotion = await self.repo.get_promotion_by_id(promotion_id)
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion not found")

        is_owner = promotion.announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        update_data = data.model_dump(exclude_unset=True)
        updated_promo = await self.repo.update_promotion(promotion, update_data)
        await self.session.commit()
        return updated_promo

    async def delete_promotion(self, user: User, promotion_id: int):
        """
        Удаляет продвижение.
        """
        promotion = await self.repo.get_promotion_by_id(promotion_id)
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion not found")

        is_owner = promotion.announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        await self.repo.delete_promotion(promotion)
        await self.session.commit()
        return {"status": "deleted", "id": promotion_id}
