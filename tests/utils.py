"""tests/utils.py."""

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.announcements.models import Announcement
from src.core.enum import DealStatus


async def approve_announcement(session: AsyncSession, announcement_id: int):
    """
    Forcibly sets the announcement to ACTIVE via a direct query to the database.
    """
    stmt = (
        update(Announcement)
        .where(Announcement.id == announcement_id)
        .values(status=DealStatus.ACTIVE)
    )
    await session.execute(stmt)
    await session.commit()
