"""src/apps/admin/services/moderation_announcement.py."""

from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.announcements.repositories.announcement import AnnouncementRepository
from src.apps.announcements.schemas.announcement import (
    AnnouncementResponse,
    AnnouncementReject,
)
from src.apps.users.models import User
from src.apps.users.repositories.user_profile import UserRepository
from src.core.enum import UserRole, DealStatus
from src.core.exceptions import PermissionDeniedError, ResourceNotFoundError


class ModerationAnnouncementService:
    """Service for administrative actions."""

    def __init__(
        self,
        repo: UserRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.announcement_repo = announcement_repo
        self.session = session

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
