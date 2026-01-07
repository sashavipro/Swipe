"""src/apps/auth/announcement.py."""

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.auth.models import VerificationCode


class AuthRepository:
    """
    Repository for managing authentication data, specifically verification codes.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.
        """
        self.session = session

    async def get_verification_code(self, email: str) -> VerificationCode | None:
        """
        Retrieves a verification code entry by the associated email.
        """
        stmt = select(VerificationCode).where(VerificationCode.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_code(self, email: str):
        """
        Removes a verification code entry for the specified email.
        """
        stmt = delete(VerificationCode).where(VerificationCode.email == email)
        await self.session.execute(stmt)
