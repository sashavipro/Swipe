"""src/apps/admin/services/crud_user.py."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.admin.repositories.crud_user import CrudUserRepository
from src.apps.admin.schemas import (
    UserUpdateByAdmin,
    DeveloperCreate,
    NotaryCreate,
    AgentCreate,
    ModeratorCreate,
    SimpleUserCreate,
)
from src.apps.auth.schemas import UserCreateBase
from src.apps.users.models import User
from src.apps.users.repositories.user_profile import UserRepository
from src.apps.users.schemas.user_profile import UserResponse
from src.core.enum import UserRole
from src.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from src.core.security.password import PasswordHandler

logger = logging.getLogger(__name__)


class CrudUserService:
    """Service for administrative actions."""

    def __init__(
        self,
        repo: UserRepository,
        repo_crud_user: CrudUserRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.repo_crud_user = repo_crud_user
        self.session = session

    async def get_users(
        self, current_user: User, role: UserRole | None = None
    ) -> list[UserResponse]:
        """
        Get all users.
        Available to: MODERATOR, NOTARY.
        """
        if current_user.role not in [UserRole.MODERATOR, UserRole.NOTARY]:
            raise PermissionDeniedError()

        return await self.repo_crud_user.list_users(role=role)

    async def _create_specific_role(
        self, moderator: User, data: UserCreateBase, role: UserRole
    ) -> UserResponse:
        """
        Internal method to create a user with a specific role.
        """
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        hashed_password = PasswordHandler.get_password_hash(data.password)
        new_user = await self.repo.create_user(data, hashed_password, role=role)
        await self.session.commit()

        logger.info(
            "User %s (Role: %s) created by moderator %s",
            new_user.id,
            role.value,
            moderator.id,
        )
        return new_user

    async def update_user_by_moderator(
        self, moderator: User, user_id: int, data: UserUpdateByAdmin
    ) -> UserResponse:
        """Edit user."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        target_user = await self.repo.get_by_id(user_id)
        if not target_user:
            raise ResourceNotFoundError()

        update_data = data.model_dump(exclude_unset=True)
        updated_user = await self.repo.update_user(target_user, update_data)
        await self.session.commit()
        return updated_user

    async def create_developer(
        self, moderator: User, data: DeveloperCreate
    ) -> UserResponse:
        """Create Developer."""
        return await self._create_specific_role(moderator, data, UserRole.DEVELOPER)

    async def create_notary(self, moderator: User, data: NotaryCreate) -> UserResponse:
        """Create Notary."""
        return await self._create_specific_role(moderator, data, UserRole.NOTARY)

    async def create_agent(self, moderator: User, data: AgentCreate) -> UserResponse:
        """Create Agent."""
        return await self._create_specific_role(moderator, data, UserRole.AGENT)

    async def create_moderator(
        self, moderator: User, data: ModeratorCreate
    ) -> UserResponse:
        """Create new Moderator."""
        return await self._create_specific_role(moderator, data, UserRole.MODERATOR)

    async def create_simple_user(
        self, moderator: User, data: SimpleUserCreate
    ) -> UserResponse:
        """Manually create a simple User (without email verification, etc.)."""
        return await self._create_specific_role(moderator, data, UserRole.USER)

    async def delete_user_by_moderator(self, moderator: User, user_id: int):
        """Delete user."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        if moderator.id == user_id:
            raise PermissionDeniedError()

        target_user = await self.repo.get_by_id(user_id)
        if not target_user:
            raise ResourceNotFoundError()

        await self.repo_crud_user.delete_user(target_user)
        await self.session.commit()
        return {"status": "deleted", "user_id": user_id}
