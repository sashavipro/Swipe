"""src/apps/admin/services/blacklist.py."""

from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.admin.repositories.blacklist import BlacklistRepository
from src.apps.users.models import User
from src.apps.users.repositories.user_profile import UserRepository
from src.core.enum import UserRole
from src.core.exceptions import PermissionDeniedError, ResourceNotFoundError


class BlacklistService:
    """Service for administrative actions"""

    def __init__(
        self,
        repo: BlacklistRepository,
        repo_user: UserRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.repo_user = repo_user
        self.session = session

    async def ban_user(self, moderator: User, user_id: int):
        """Ban user."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        if moderator.id == user_id:
            raise PermissionDeniedError()

        target_user = await self.repo_user.get_by_id(user_id)
        if not target_user:
            raise ResourceNotFoundError()

        await self.repo.add_to_blacklist(moderator.id, user_id)
        await self.session.commit()
        return {"status": "banned", "user_id": user_id}

    async def unban_user(self, moderator: User, user_id: int):
        """Unban user."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        await self.repo.remove_from_blacklist(user_id)
        await self.session.commit()
        return {"status": "unbanned", "user_id": user_id}
