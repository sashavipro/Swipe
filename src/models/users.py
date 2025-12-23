""" "src/models/users.py."""

import enum
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from datetime import date, datetime, timezone

from sqlalchemy import String, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, IntPK, CreatedAt

if TYPE_CHECKING:
    from src.models.real_estate import Announcement

USER_ID_FK = "users.id"


class UserRole(str, enum.Enum):
    """Роли пользователя."""

    # pylint: disable=too-few-public-methods

    USER = "user"
    AGENT = "agent"
    DEVELOPER = "developer"
    MODERATOR = "moderator"
    NOTARY = "notary"


class NotificationType(str, enum.Enum):
    """Тип уведомлений."""

    # pylint: disable=too-few-public-methods

    ME = "me"
    ME_AND_AGENT = "me_and_agent"
    AGENT = "agent"
    OFF = "off"


class ComplaintReason(str, enum.Enum):
    """Причины жалобы."""

    # pylint: disable=too-few-public-methods

    SPAM = "spam"
    SCAM = "scam"
    INSULT = "insult"
    OTHER = "other"


class Complaint(Base):
    """
    Модель жалобы на пользователя.
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
    Контакты агента, привязанные к конкретному юзеру.
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
    """Модель пользователя."""

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
        "Subscription", back_populates="user", uselist=False
    )

    saved_searches: Mapped[List["SavedSearch"]] = relationship(
        "SavedSearch", back_populates="user"
    )

    blacklist: Mapped[List["BlackList"]] = relationship(
        "BlackList", foreign_keys="[BlackList.user_id]", back_populates="user"
    )

    favorites: Mapped[List["Chosen"]] = relationship("Chosen", back_populates="user")

    sent_messages: Mapped[List["Message"]] = relationship(
        "Message", foreign_keys="[Message.sender_id]", back_populates="sender"
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message", foreign_keys="[Message.recipient_id]", back_populates="recipient"
    )

    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="owner"
    )

    agent_contact: Mapped[Optional["AgentContact"]] = relationship(
        "AgentContact",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    complaints_filed: Mapped[List["Complaint"]] = relationship(
        "Complaint", foreign_keys="[Complaint.reporter_id]", back_populates="reporter"
    )
    complaints_received: Mapped[List["Complaint"]] = relationship(
        "Complaint",
        foreign_keys="[Complaint.reported_user_id]",
        back_populates="reported_user",
    )


class Subscription(Base):
    """Подписка пользователя."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "subscriptions"

    id: Mapped[IntPK]
    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK), unique=True)

    paid_to: Mapped[date]
    auto_renewal: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship("User", back_populates="subscription")


class BlackList(Base):
    """Черный список пользователя."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "blacklist"

    id: Mapped[IntPK]

    # Тот, КТО блокирует
    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    # Тот, КОГО блокируют
    blocked_user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK))

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="blacklist"
    )


class PropertyType(str, enum.Enum):
    """Тип недвижимости."""

    SECONDARY = "secondary"
    NEW_BUILDINGS = "new buildings"
    COTTAGE = "cottage"


class ConstructionStatus(str, enum.Enum):
    """Статус строительства."""

    READY = "ready"
    NOT_READY = "not ready"


class Purpose(str, enum.Enum):
    """Назначение."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"


class PurchaseTerms(str, enum.Enum):
    """Условия покупки."""

    MORTGAGE = "mortgage"
    CASH = "cash"
    INSTALLMENT = "installment"
    MATERNAL_CAPITAL = "maternal_capital"


class Condition(str, enum.Enum):
    """Состояние ремонта."""

    RENOVATED = "renovated"
    DESIGNER = "designer"
    ROUGH = "rough"
    WHITE_BOX = "white_box"
    NEEDS_REPAIR = "needs_repair"


class SavedSearch(Base):
    """
    Таблица сохраненных фильтров.
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
    """Сообщение в чате."""

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


class Chosen(Base):
    """Избранное объявление."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "chosen"

    user_id: Mapped[int] = mapped_column(ForeignKey(USER_ID_FK), primary_key=True)
    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id"), primary_key=True
    )

    created_at: Mapped[CreatedAt]

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="favorited_by"
    )


class VerificationCode(Base):
    """
    Таблица для хранения временных SMS-кодов.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "verification_codes"

    id: Mapped[IntPK]
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(6))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    expires_at: Mapped[datetime]

    @property
    def is_expired(self) -> bool:
        """Проверяет, истек ли срок действия кода."""
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.expires_at
