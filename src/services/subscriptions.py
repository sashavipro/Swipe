"""src/services/subscriptions.py."""

from datetime import timedelta, date
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.subscriptions import SubscriptionRepository
from src.models.users import Subscription
from src.schemas.users import SubscriptionResponse


class SubscriptionService:
    """
    Сервис для работы с подпиской.
    """

    def __init__(self, repo: SubscriptionRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def toggle_auto_renewal(self, user_id: int) -> SubscriptionResponse:
        """Вкл/Выкл автопродления"""
        user = await self.repo.get_by_id_with_subscription(user_id)
        if not user.subscription:
            raise HTTPException(status_code=400, detail="No active subscription")

        user.subscription.auto_renewal = not user.subscription.auto_renewal
        self.session.add(user.subscription)
        await self.session.commit()
        return user.subscription

    async def extend_subscription(
        self, user_id: int, days: int = 30
    ) -> SubscriptionResponse:
        """Продление подписки"""
        user = await self.repo.get_by_id_with_subscription(user_id)

        if user.subscription:
            start_date = max(user.subscription.paid_to, date.today())
            user.subscription.paid_to = start_date + timedelta(days=days)
        else:
            new_sub = Subscription(
                user_id=user_id,
                paid_to=date.today() + timedelta(days=days),
                auto_renewal=True,
            )
            self.session.add(new_sub)
            user.subscription = new_sub

        await self.session.commit()
        await self.session.refresh(user, ["subscription"])
        return user.subscription
