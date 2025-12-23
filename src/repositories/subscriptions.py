"""src/repositories/subscriptions.py."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.users import User

logger = logging.getLogger(__name__)


class SubscriptionRepository:
    """
    Репозиторий для работы с подпиской.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_with_subscription(self, user_id: int) -> User | None:
        """
        Получить юзера вместе с данными о подписке.
        Возвращает None, если пользователь не найден.
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
