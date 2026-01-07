"""src/apps/admin/repositories/blacklist.py."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.users.models import BlackList


class BlacklistRepository:
    """
    Repository for working with blacklist.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_to_blacklist(self, admin_id: int, user_id: int):
        """Adds a user to the blacklist."""
        stmt = select(BlackList).where(BlackList.blocked_user_id == user_id)
        if (await self.session.execute(stmt)).scalar_one_or_none():
            return

        entry = BlackList(user_id=admin_id, blocked_user_id=user_id)
        self.session.add(entry)
        await self.session.flush()

    async def remove_from_blacklist(self, user_id: int):
        """Removes a user from the blacklist."""
        stmt = select(BlackList).where(BlackList.blocked_user_id == user_id)
        result = await self.session.execute(stmt)
        entry = result.scalar_one_or_none()

        if entry:
            await self.session.delete(entry)
            await self.session.flush()
