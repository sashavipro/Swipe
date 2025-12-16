"""src/models/real_estate.py."""

import enum
from typing import List, Optional, TYPE_CHECKING
from datetime import date

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Integer,
    Text,
    Float,
    Date,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, IntPK, CreatedAt, UpdatedAt

if TYPE_CHECKING:
    from src.models.users import User, Chosen

CASCADE_ALL_DELETE = "all, delete-orphan"

announcement_images_association = Table(
    "announcement_images_association",
    Base.metadata,
    Column("announcement_id", ForeignKey("announcements.id"), primary_key=True),
    Column("image_id", ForeignKey("images.id"), primary_key=True),
)


class DealStatus(str, enum.Enum):
    """Статус сделки."""

    ACTIVE = "active"
    SOLD = "sold"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class RoomCount(str, enum.Enum):
    """Количество комнат."""

    STUDIO = "studio"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR_PLUS = "4+"


class CommunicationMethod(str, enum.Enum):
    """Способ связи."""

    CALL = "call"
    MESSAGE = "message"
    ANY = "any"


class HouseType(str, enum.Enum):
    """Тип дома."""

    MONOLITHIC = "monolithic"
    PANEL = "panel"
    BRICK = "brick"
    BLOCK = "block"


class HouseClass(str, enum.Enum):
    """Класс жилья."""

    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    ELITE = "elite"


class ConstructionTechnology(str, enum.Enum):
    """Технология строительства."""

    MONOLITH = "monolith"
    BRICK = "brick"


class TerritoryType(str, enum.Enum):
    """Тип территории."""

    CLOSED = "closed"
    OPEN = "open"


class Utilities(str, enum.Enum):
    """Коммуникации."""

    CENTRAL = "central"
    AUTONOMOUS = "autonomous"


class GasType(str, enum.Enum):
    """Газоснабжение."""

    MAIN = "main"
    NONE = "none"


class HeatingType(str, enum.Enum):
    """Отопление."""

    CENTRAL = "central"
    GAS = "gas"
    ELECTRIC = "electric"


class SewerageType(str, enum.Enum):
    """Канализация."""

    CENTRAL = "central"
    SEPTIC = "septic"


class WaterSupplyType(str, enum.Enum):
    """Водоснабжение."""

    CENTRAL = "central"
    WELL = "well"


class LayoutType(str, enum.Enum):
    """Тип планировки."""

    ISOLATED = "isolated"
    ADJACENT = "adjacent"
    STUDIO = "studio"


class News(Base):
    """Новости ЖК."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "news"
    id: Mapped[IntPK]
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)
    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="news"
    )


class Document(Base):
    """Документы ЖК."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "documents"
    id: Mapped[IntPK]
    is_excel: Mapped[bool] = mapped_column(Boolean, default=False)
    doc_url: Mapped[str] = mapped_column(String)
    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="document"
    )


class House(Base):
    """Жилой комплекс (Дом)."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "houses"
    id: Mapped[IntPK]
    name: Mapped[str] = mapped_column(String)
    sections: Mapped[List["Section"]] = relationship(
        "Section", back_populates="house", cascade=CASCADE_ALL_DELETE
    )


class Section(Base):
    """Секция (подъезд)."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "sections"
    id: Mapped[IntPK]
    house_id: Mapped[int] = mapped_column(ForeignKey("houses.id"))
    name: Mapped[str] = mapped_column(String)
    house: Mapped["House"] = relationship("House", back_populates="sections")
    floors: Mapped[List["Floor"]] = relationship(
        "Floor", back_populates="section", cascade=CASCADE_ALL_DELETE
    )


class Floor(Base):
    """Этаж."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "floors"
    id: Mapped[IntPK]
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    number: Mapped[int] = mapped_column(Integer)
    section: Mapped["Section"] = relationship("Section", back_populates="floors")
    apartments: Mapped[List["Apartment"]] = relationship(
        "Apartment", back_populates="floor", cascade=CASCADE_ALL_DELETE
    )


class Apartment(Base):
    """
    Физическая квартира.
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "apartments"

    id: Mapped[IntPK]
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))

    floor: Mapped["Floor"] = relationship("Floor", back_populates="apartments")

    announcement: Mapped[Optional["Announcement"]] = relationship(
        "Announcement", back_populates="apartment_unit", uselist=False
    )


class Announcement(Base):
    """Объявление о продаже"""

    # pylint: disable=too-few-public-methods
    __tablename__ = "announcements"

    id: Mapped[IntPK]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    apartment_id: Mapped[int] = mapped_column(ForeignKey("apartments.id"), unique=True)

    apartment_number: Mapped[int] = mapped_column(Integer)
    area: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    description: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[str] = mapped_column(String)

    status: Mapped[DealStatus] = mapped_column(default=DealStatus.ACTIVE)

    house_type: Mapped[Optional[HouseType]] = mapped_column(nullable=True)
    house_class: Mapped[Optional[HouseClass]] = mapped_column(nullable=True)
    construction_technology: Mapped[Optional[ConstructionTechnology]] = mapped_column(
        nullable=True
    )
    territory: Mapped[Optional[TerritoryType]] = mapped_column(nullable=True)
    distance_to_sea: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    utilities: Mapped[Optional[Utilities]] = mapped_column(nullable=True)
    ceiling_height: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gas: Mapped[Optional[GasType]] = mapped_column(nullable=True)
    heating: Mapped[Optional[HeatingType]] = mapped_column(nullable=True)
    sewerage: Mapped[Optional[SewerageType]] = mapped_column(nullable=True)
    water_supply: Mapped[Optional[WaterSupplyType]] = mapped_column(nullable=True)

    registration: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    calculation_options: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    purpose: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sum_in_contract: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    founding_document: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    number_of_rooms: Mapped[RoomCount] = mapped_column(default=RoomCount.ONE)
    layout: Mapped[Optional[LayoutType]] = mapped_column(nullable=True)
    residential_condition: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    kitchen_area: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    has_balcony: Mapped[bool] = mapped_column(default=False)

    agent_commission: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    communication_method: Mapped[CommunicationMethod] = mapped_column(
        default=CommunicationMethod.ANY
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    news_id: Mapped[Optional[int]] = mapped_column(ForeignKey("news.id"), nullable=True)
    document_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )

    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    owner: Mapped["User"] = relationship("User", back_populates="announcements")
    apartment_unit: Mapped["Apartment"] = relationship(
        "Apartment", back_populates="announcement"
    )
    news: Mapped[Optional["News"]] = relationship(
        "News", back_populates="announcements"
    )
    document: Mapped[Optional["Document"]] = relationship(
        "Document", back_populates="announcements"
    )
    images: Mapped[List["Image"]] = relationship(
        "Image", secondary=announcement_images_association
    )
    promotion: Mapped[Optional["Promotion"]] = relationship(
        "Promotion",
        back_populates="announcement",
        uselist=False,
        cascade="all, delete-orphan",
    )
    favorited_by: Mapped[List["Chosen"]] = relationship(
        "Chosen", back_populates="announcement"
    )


class Promotion(Base):
    """Платное продвижение"""

    # pylint: disable=too-few-public-methods
    __tablename__ = "promotions"

    id: Mapped[IntPK]
    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id"), unique=True
    )

    is_turbo: Mapped[bool] = mapped_column(default=False)
    is_colored: Mapped[bool] = mapped_column(default=False)
    is_large: Mapped[bool] = mapped_column(default=False)
    is_raised: Mapped[bool] = mapped_column(default=False)
    add_phrase: Mapped[bool] = mapped_column(default=False)

    phrase_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    color_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    price_turbo: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_color: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_large: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_raised: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_phrase: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="promotion"
    )


class Image(Base):
    """Изображение."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "images"
    id: Mapped[IntPK]
    image_url: Mapped[str] = mapped_column(String)
