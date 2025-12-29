"""src/services/admin.py."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.security.password import PasswordHandler
from src.models.real_estate import DealStatus
from src.models.users import User, UserRole
from src.repositories.announcements import AnnouncementRepository
from src.repositories.users import UserRepository
from src.common.exceptions import PermissionDeniedError, ResourceNotFoundError
from src.schemas.real_estate import AnnouncementResponse, AnnouncementReject
from src.schemas.users import (
    UserUpdateByAdmin,
    UserResponse,
    ComplaintCreate,
    ComplaintResponse,
    DeveloperCreate,
    NotaryCreate,
    AgentCreate,
    ModeratorCreate,
    SimpleUserCreate,
    UserCreateBase,
)

logger = logging.getLogger(__name__)


class AdminService:
    """Service for administrative actions (ban, moderation, complaints)."""

    def __init__(
        self,
        repo: UserRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.announcement_repo = announcement_repo
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

        return await self.repo.list_users(role=role)

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

        await self.repo.delete_user(target_user)
        await self.session.commit()
        return {"status": "deleted", "user_id": user_id}

    async def ban_user(self, moderator: User, user_id: int):
        """Ban user."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        if moderator.id == user_id:
            raise PermissionDeniedError()

        target_user = await self.repo.get_by_id(user_id)
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

    async def report_user(
        self, reporter: User, data: ComplaintCreate
    ) -> ComplaintResponse:
        """Report a user (available to everyone)."""
        if reporter.id == data.reported_user_id:
            raise PermissionDeniedError()

        target = await self.repo.get_by_id(data.reported_user_id)
        if not target:
            raise ResourceNotFoundError()

        complaint = await self.repo.create_complaint(reporter.id, data)
        await self.session.commit()
        return complaint

    async def get_complaints(self, moderator: User) -> list[ComplaintResponse]:
        """View complaints (Moderator only)."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        return await self.repo.list_complaints(resolved=False)

    async def resolve_complaint(self, moderator: User, complaint_id: int):
        """Close complaint (Moderator only)."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError()

        await self.repo.resolve_complaint(complaint_id)
        await self.session.commit()
        return {"status": "resolved"}

    async def get_pending_announcements(
        self, moderator: User
    ) -> list[AnnouncementResponse]:
        """Get announcements pending moderation."""
        if moderator.role not in [UserRole.MODERATOR]:
            raise PermissionDeniedError()

        return await self.announcement_repo.get_announcements(status=DealStatus.PENDING)

    async def approve_announcement(self, moderator: User, announcement_id: int):
        """Approve announcement."""
        if moderator.role not in [UserRole.MODERATOR]:
            raise PermissionDeniedError()

        announcement = await self.announcement_repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError()

        await self.announcement_repo.change_status(announcement, DealStatus.ACTIVE)
        await self.session.commit()
        return {"status": "approved", "id": announcement_id}

    async def reject_announcement(
        self, moderator: User, announcement_id: int, data: AnnouncementReject
    ):
        """Reject announcement."""
        if moderator.role not in [UserRole.MODERATOR]:
            raise PermissionDeniedError()

        announcement = await self.announcement_repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError()

        await self.announcement_repo.change_status(
            announcement, DealStatus.REJECTED, rejection_reason=data.reason
        )
        await self.session.commit()
        return {"status": "rejected", "id": announcement_id}
