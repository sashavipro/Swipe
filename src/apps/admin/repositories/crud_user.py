"""src/apps/admin/repositories/crud_user.py."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.users.models import User
from src.core.enum import UserRole


class CrudUserRepository:
    """
    Repository for working with users.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_users(self, role: UserRole | None = None) -> list[User]:
        """
        Returns a list of users.
        If a role is provided, filters by it.
        """
        stmt = select(User).order_by(User.id)

        if role:
            stmt = stmt.where(User.role == role)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_user(self, user: User) -> None:
        """Deletes a user."""
        await self.session.delete(user)
        await self.session.flush()
