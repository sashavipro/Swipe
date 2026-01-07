"""src/apps/auth/models.py."""

from datetime import datetime, timezone
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models.base import Base, IntPK


class VerificationCode(Base):
    """
    Table for storing temporary SMS codes.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "verification_codes"

    id: Mapped[IntPK]
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=True
    )
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(6))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    expires_at: Mapped[datetime]

    @property
    def is_expired(self) -> bool:
        """Checks if the code has expired."""
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.expires_at
