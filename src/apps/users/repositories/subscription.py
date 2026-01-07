"""src/apps/users/repositories/subscription.py."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.apps.users.models import User

logger = logging.getLogger(__name__)


class SubscriptionRepository:
    """
    Repository for working with subscriptions.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_with_subscription(self, user_id: int) -> User | None:
        """
        Get user with subscription data.
        Returns None if user is not found.
        """
        logger.debug("Fetching subscription data for user_id=%s", user_id)

        query = (
            select(User)
            .options(selectinload(User.subscription))
            .where(User.id == user_id)
        )

        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            logger.debug(
                "Found user %s (has_subscription=%s)", user_id, bool(user.subscription)
            )
        else:
            logger.debug("User %s not found during subscription lookup", user_id)

        return user
