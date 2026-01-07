"""src/apps/users/services/complaint.py."""

from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.users.models import User
from src.apps.users.repositories.complaint import ComplaintRepository
from src.apps.users.repositories.user_profile import UserRepository
from src.apps.users.schemas.complaint import ComplaintCreate, ComplaintResponse
from src.core.enum import UserRole
from src.core.exceptions import PermissionDeniedError, ResourceNotFoundError


class ComplaintService:
    """
    Service for working with complaints.
    """

    def __init__(
        self,
        repo: ComplaintRepository,
        repo_user: UserRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.repo_user = repo_user
        self.session = session

    async def report_user(
        self, reporter: User, data: ComplaintCreate
    ) -> ComplaintResponse:
        """Report a user (available to everyone)."""
        if reporter.id == data.reported_user_id:
            raise PermissionDeniedError()

        target = await self.repo_user.get_by_id(data.reported_user_id)
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
