"""src/apps/users/repositories/complaint.py."""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.users.models import Complaint
from src.apps.users.schemas.complaint import ComplaintCreate

logger = logging.getLogger(__name__)


class ComplaintRepository:
    """
    Repository for working with complaint.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_complaint(
        self,
        reporter_id: int,
        data: ComplaintCreate,
    ) -> Complaint:
        """Creates a new complaint against a user."""
        complaint = Complaint(
            reporter_id=reporter_id,
            reported_user_id=data.reported_user_id,
            reason=data.reason,
            description=data.description,
        )
        self.session.add(complaint)
        await self.session.flush()
        return complaint

    async def list_complaints(self, resolved: bool = False) -> list[Complaint]:
        """List complaints (default: active/unresolved only)."""
        stmt = (
            select(Complaint)
            .where(Complaint.is_resolved == resolved)
            .order_by(Complaint.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def resolve_complaint(self, complaint_id: int):
        """Mark a complaint as resolved."""
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        result = await self.session.execute(stmt)
        complaint = result.scalar_one_or_none()
        if complaint:
            complaint.is_resolved = True
            await self.session.flush()
