"""src/apps/users/models.py."""

from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from datetime import date
from sqlalchemy import String, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.enum import (
    UserRole,
    NotificationType,
    ComplaintReason,
    Purpose,
    PurchaseTerms,
    Condition,
    ConstructionStatus,
    PropertyType,
)
from src.core.models.base import Base, IntPK, CreatedAt


if TYPE_CHECKING:
    from src.apps.announcements.models import Announcement


USER_ID_FK = "users.id"
CASCADE_ALL_DELETE = "all, delete-orphan"


class Complaint(Base):
    """
    User complaint model.
    """

    # pylint: disable=too-few-public-methods

    __tablename__ = "complaints"

    id: Mapped[IntPK]

    reporter_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    reported_user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    reason: Mapped[ComplaintReason] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_resolved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[CreatedAt]

    reporter: Mapped["User"] = relationship(
        "User", foreign_keys=[reporter_id], back_populates="complaints_filed"
    )
    reported_user: Mapped["User"] = relationship(
        "User", foreign_keys=[reported_user_id], back_populates="complaints_received"
    )


class AgentContact(Base):
    """
    Agent contacts linked to a specific user.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "agent_contacts"

    id: Mapped[IntPK]
    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK), unique=True)

    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="agent_contact")


class User(Base):
    """User model."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "users"

    id: Mapped[IntPK]

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    notification_type: Mapped[NotificationType] = mapped_column(
        default=NotificationType.ME
    )

    notification_transfer: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[CreatedAt]

    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="user", uselist=False, cascade=CASCADE_ALL_DELETE
    )

    saved_searches: Mapped[List["SavedSearch"]] = relationship(
        "SavedSearch", back_populates="user", cascade=CASCADE_ALL_DELETE
    )

    blacklist: Mapped[List["BlackList"]] = relationship(
        "BlackList", foreign_keys="[BlackList.user_id]", back_populates="user"
    )

    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="user", cascade=CASCADE_ALL_DELETE
    )

    sent_messages: Mapped[List["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.sender_id]",
        back_populates="sender",
        cascade=CASCADE_ALL_DELETE,
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.recipient_id]",
        back_populates="recipient",
        cascade=CASCADE_ALL_DELETE,
    )

    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="owner", cascade=CASCADE_ALL_DELETE
    )

    agent_contact: Mapped[Optional["AgentContact"]] = relationship(
        "AgentContact",
        back_populates="user",
        uselist=False,
        cascade=CASCADE_ALL_DELETE,
        lazy="selectin",
    )

    complaints_filed: Mapped[List["Complaint"]] = relationship(
        "Complaint",
        foreign_keys="[Complaint.reporter_id]",
        back_populates="reporter",
        cascade=CASCADE_ALL_DELETE,
    )
    complaints_received: Mapped[List["Complaint"]] = relationship(
        "Complaint",
        foreign_keys="[Complaint.reported_user_id]",
        back_populates="reported_user",
        cascade=CASCADE_ALL_DELETE,
    )


class Subscription(Base):
    """User subscription."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "subscriptions"

    id: Mapped[IntPK]
    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK), unique=True)

    paid_to: Mapped[date]
    auto_renewal: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship("User", back_populates="subscription")


class BlackList(Base):
    """User blacklist."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "blacklist"

    id: Mapped[IntPK]

    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    blocked_user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="blacklist"
    )


class SavedSearch(Base):
    """
    Saved search filters table.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "saved_searches"

    id: Mapped[IntPK]
    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    type_secondary: Mapped[bool] = mapped_column(default=False)
    type_new_buildings: Mapped[bool] = mapped_column(default=False)
    type_cottage: Mapped[bool] = mapped_column(default=False)

    type_of_property: Mapped[Optional[PropertyType]] = mapped_column(nullable=True)
    status_house: Mapped[Optional[ConstructionStatus]] = mapped_column(nullable=True)

    district: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    microdistrict: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    number_of_rooms: Mapped[Optional[int]] = mapped_column(nullable=True)

    price_from: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    price_to: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)

    area_to: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    area_from: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    purpose: Mapped[Optional[Purpose]] = mapped_column(nullable=True)
    purchase_terms: Mapped[Optional[PurchaseTerms]] = mapped_column(nullable=True)
    condition: Mapped[Optional[Condition]] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="saved_searches")


class Message(Base):
    """Chat message."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "messages"

    id: Mapped[IntPK]
    sender_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))
    recipient_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    content: Mapped[Optional[str]] = mapped_column(Text)
    file_url: Mapped[Optional[str]] = mapped_column(String)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[CreatedAt]

    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    recipient: Mapped["User"] = relationship(
        "User", foreign_keys=[recipient_id], back_populates="received_messages"
    )


class Favorite(Base):
    """Favorite announcement."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK), primary_key=True)
    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id"), primary_key=True
    )

    created_at: Mapped[CreatedAt]

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="favorited_by"
    )
