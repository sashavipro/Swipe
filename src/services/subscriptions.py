"""src/services/subscriptions.py."""

import logging
from datetime import timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import ResourceNotFoundError
from src.repositories.subscriptions import SubscriptionRepository
from src.models.users import Subscription
from src.schemas.users import SubscriptionResponse

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Service for subscription management.
    """

    def __init__(self, repo: SubscriptionRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def toggle_auto_renewal(self, user_id: int) -> SubscriptionResponse:
        """Toggle auto-renewal on/off."""
        logger.info("Toggling auto-renewal for user %s", user_id)

        user = await self.repo.get_by_id_with_subscription(user_id)
        if not user:
            logger.warning("User %s not found during subscription toggle", user_id)
            raise ResourceNotFoundError()

        if not user.subscription:
            logger.warning("No active subscription for user %s", user_id)
            raise ResourceNotFoundError()

        user.subscription.auto_renewal = not user.subscription.auto_renewal
        self.session.add(user.subscription)
        await self.session.commit()

        logger.info(
            "Auto-renewal set to %s for user %s",
            user.subscription.auto_renewal,
            user_id,
        )
        return user.subscription

    async def extend_subscription(
        self, user_id: int, days: int = 30
    ) -> SubscriptionResponse:
        """Extend subscription."""
        logger.info("Extending subscription for user %s by %s days", user_id, days)

        user = await self.repo.get_by_id_with_subscription(user_id)
        if not user:
            logger.warning("User %s not found during subscription extension", user_id)
            raise ResourceNotFoundError()

        if user.subscription:
            start_date = max(user.subscription.paid_to, date.today())
            user.subscription.paid_to = start_date + timedelta(days=days)
            logger.info("Subscription extended until %s", user.subscription.paid_to)
        else:
            new_sub = Subscription(
                user_id=user_id,
                paid_to=date.today() + timedelta(days=days),
                auto_renewal=True,
            )
            self.session.add(new_sub)
            user.subscription = new_sub
            logger.info("New subscription created until %s", new_sub.paid_to)

        await self.session.commit()
        await self.session.refresh(user, ["subscription"])
        return user.subscription
