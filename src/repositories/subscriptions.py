"""src/repositories/subscriptions.py."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.users import User


class SubscriptionRepository:
    """
    Репозиторий для работы с подпиской.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_with_subscription(self, user_id: int) -> User | None:
        """Получить юзера вместе с данными о подписке."""
        query = (
            select(User)
            .options(selectinload(User.subscription))
            .where(User.id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
