import enum
from typing import List, Optional, TYPE_CHECKING
from datetime import date

from sqlalchemy import String, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, int_pk, created_at

if TYPE_CHECKING:
    from src.models.real_estate import Announcement


class UserRole(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    DEVELOPER = "developer"
    MODERATOR = "moderator"
    NOTARY = "notary"


class NotificationType(str, enum.Enum):
    ME = "me"
    ME_AND_AGENT = "me_and_agent"
    AGENT = "agent"
    OFF = "off"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]

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

    created_at: Mapped[created_at]

    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="user", uselist=False
    )

    saved_searches: Mapped[List["SavedSearch"]] = relationship(
        "SavedSearch", back_populates="user"
    )

    blacklist: Mapped[List["BlackList"]] = relationship(
        "BlackList", back_populates="user"
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


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    paid_to: Mapped[date]
    auto_renewal: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship("User", back_populates="subscription")


class BlackList(Base):
    __tablename__ = "blacklist"

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    blocked_user_id: Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship("User", back_populates="blacklist")


class PropertyType(str, enum.Enum):
    SECONDARY = "secondary"
    NEW_BUIlDINGS = "new buildings"
    COTTAGE = "cottage"


class ConstructionStatus(str, enum.Enum):
    READY = "ready"
    NOT_READY = "not ready"


class Purpose(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"


class PurchaseTerms(str, enum.Enum):
    MORTGAGE = "mortgage"  # Ипотека
    CASH = "cash"  # Наличные
    INSTALLMENT = "installment"  # Рассрочка
    MATERNAL_CAPITAL = "maternal_capital"  # Мат. капитал


class Condition(str, enum.Enum):
    RENOVATED = "renovated"  # Евроремонт
    DESIGNER = "designer"  # Дизайнерский
    ROUGH = "rough"  # Черновая
    WHITE_BOX = "white_box"  # Предчистовая
    NEEDS_REPAIR = "needs_repair"  # Требует ремонта


class SavedSearch(Base):
    """
    Filter table.
    """

    __tablename__ = "saved_searches"

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    type_secondary: Mapped[bool] = mapped_column(default=False)  # Вторичка
    type_new_buildings: Mapped[bool] = mapped_column(default=False)  # Новостройки
    type_cottage: Mapped[bool] = mapped_column(default=False)  # Коттеджи

    type_of_property: Mapped[Optional[PropertyType]] = mapped_column(nullable=True)

    status_house: Mapped[Optional[ConstructionStatus]] = mapped_column(nullable=True)

    district: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    microdistrict: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    number_of_rooms: Mapped[Optional[int]] = mapped_column(nullable=True)

    price_from: Mapped[Optional[float]] = mapped_column(nullable=True)
    price_to: Mapped[Optional[float]] = mapped_column(nullable=True)

    area_to: Mapped[Optional[float]] = mapped_column(nullable=True)
    area_from: Mapped[Optional[float]] = mapped_column(nullable=True)

    purpose: Mapped[Optional[Purpose]] = mapped_column(nullable=True)
    purchase_terms: Mapped[Optional[PurchaseTerms]] = mapped_column(nullable=True)
    condition: Mapped[Optional[Condition]] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="saved_searches")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int_pk]
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    content: Mapped[Optional[str]] = mapped_column(Text)
    file_url: Mapped[Optional[str]] = mapped_column(String)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]

    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    recipient: Mapped["User"] = relationship(
        "User", foreign_keys=[recipient_id], back_populates="received_messages"
    )


class Chosen(Base):
    __tablename__ = "chosen"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id"), primary_key=True
    )

    created_at: Mapped[created_at]

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="favorited_by"
    )
