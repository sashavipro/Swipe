"""src/models/real_estate.py."""

import enum
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from datetime import date

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Integer,
    Text,
    Date,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.orderinglist import ordering_list

from src.models.base import Base, IntPK, CreatedAt, UpdatedAt

if TYPE_CHECKING:
    from src.models.users import User, Chosen

CASCADE_ALL_DELETE = "all, delete-orphan"
ANNOUNCEMENTS_ID_FK = "announcements.id"
HOUSES_ID_FK = "houses.id"


class DealStatus(str, enum.Enum):
    """Статус сделки."""

    PENDING = "pending"
    ACTIVE = "active"
    SOLD = "sold"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class RequestStatus(str, enum.Enum):
    """Статус заявки на добавление в шахматку."""

    PENDING = "pending"
    APPROVED = "approved"
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
    house_id: Mapped[Optional[int]] = mapped_column(ForeignKey(HOUSES_ID_FK))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)

    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="news"
    )
    house: Mapped["House"] = relationship("House", back_populates="news")


class Document(Base):
    """Документы ЖК."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "documents"
    id: Mapped[IntPK]
    house_id: Mapped[Optional[int]] = mapped_column(ForeignKey(HOUSES_ID_FK))
    is_excel: Mapped[bool] = mapped_column(Boolean, default=False)
    doc_url: Mapped[str] = mapped_column(String)

    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="document"
    )
    house: Mapped["House"] = relationship("House", back_populates="documents")


class HouseInfo(Base):
    """
    Детальная информация о ЖК (Карточка ЖК).
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "house_infos"

    id: Mapped[int] = mapped_column(ForeignKey(HOUSES_ID_FK), primary_key=True)

    main_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    description: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(String)
    district: Mapped[Optional[str]] = mapped_column(String)
    microdistrict: Mapped[Optional[str]] = mapped_column(String)

    latitude: Mapped[Optional[str]] = mapped_column(String)
    longitude: Mapped[Optional[str]] = mapped_column(String)

    house_type: Mapped[Optional[HouseType]] = mapped_column(nullable=True)
    house_class: Mapped[Optional[HouseClass]] = mapped_column(nullable=True)
    construction_technology: Mapped[Optional[ConstructionTechnology]] = mapped_column(
        nullable=True
    )
    territory: Mapped[Optional[TerritoryType]] = mapped_column(nullable=True)
    distance_to_sea: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ceiling_height: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )

    utilities: Mapped[Optional[Utilities]] = mapped_column(nullable=True)
    gas: Mapped[Optional[GasType]] = mapped_column(nullable=True)
    heating: Mapped[Optional[HeatingType]] = mapped_column(nullable=True)
    sewerage: Mapped[Optional[SewerageType]] = mapped_column(nullable=True)
    water_supply: Mapped[Optional[WaterSupplyType]] = mapped_column(nullable=True)
    electricity: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    payment_options: Mapped[Optional[str]] = mapped_column(String)
    legal_terms: Mapped[Optional[str]] = mapped_column(String)

    house: Mapped["House"] = relationship("House", back_populates="info")


class House(Base):
    """Жилой комплекс (Дом)."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "houses"
    id: Mapped[IntPK]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)

    sections: Mapped[List["Section"]] = relationship(
        "Section", back_populates="house", cascade=CASCADE_ALL_DELETE
    )
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])

    info: Mapped[Optional["HouseInfo"]] = relationship(
        "HouseInfo", back_populates="house", uselist=False, cascade=CASCADE_ALL_DELETE
    )

    news: Mapped[List["News"]] = relationship("News", back_populates="house")
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="house"
    )


class Section(Base):
    """Секция (подъезд)."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "sections"
    id: Mapped[IntPK]
    house_id: Mapped[int] = mapped_column(ForeignKey(HOUSES_ID_FK))
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
    Физическая квартира (Ячейка в шахматке).
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "apartments"

    id: Mapped[IntPK]
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))

    number: Mapped[int] = mapped_column(Integer)

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

    apartment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("apartments.id"), unique=True, nullable=True
    )

    floor_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    apartment_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    area: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
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
    ceiling_height: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
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
    kitchen_area: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    has_balcony: Mapped[bool] = mapped_column(default=False)

    agent_commission: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2), default=0.0
    )
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
    apartment_unit: Mapped[Optional["Apartment"]] = relationship(
        "Apartment", back_populates="announcement"
    )
    news: Mapped[Optional["News"]] = relationship(
        "News", back_populates="announcements"
    )
    document: Mapped[Optional["Document"]] = relationship(
        "Document", back_populates="announcements"
    )

    images: Mapped[List["Image"]] = relationship(
        "Image",
        back_populates="announcement",
        order_by="Image.position",
        collection_class=ordering_list("position"),
        cascade=CASCADE_ALL_DELETE,
    )

    promotion: Mapped[Optional["Promotion"]] = relationship(
        "Promotion",
        back_populates="announcement",
        uselist=False,
        cascade=CASCADE_ALL_DELETE,
    )
    favorited_by: Mapped[List["Chosen"]] = relationship(
        "Chosen", back_populates="announcement"
    )
    chessboard_request: Mapped[Optional["ChessboardRequest"]] = relationship(
        "ChessboardRequest", back_populates="announcement", uselist=False
    )


class ChessboardRequest(Base):
    """
    Заявка на привязку объявления к шахматке (квартире в доме).
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "chessboard_requests"

    id: Mapped[IntPK]
    announcement_id: Mapped[int] = mapped_column(ForeignKey(ANNOUNCEMENTS_ID_FK))

    target_house_id: Mapped[int] = mapped_column(ForeignKey(HOUSES_ID_FK))
    target_section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    target_floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))
    target_apartment_number: Mapped[int] = mapped_column(Integer)

    status: Mapped[RequestStatus] = mapped_column(default=RequestStatus.PENDING)
    developer_comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="chessboard_request"
    )
    house: Mapped["House"] = relationship("House")


class Promotion(Base):
    """Платное продвижение"""

    # pylint: disable=too-few-public-methods
    __tablename__ = "promotions"

    id: Mapped[IntPK]
    announcement_id: Mapped[int] = mapped_column(
        ForeignKey(ANNOUNCEMENTS_ID_FK), unique=True
    )

    is_turbo: Mapped[bool] = mapped_column(default=False)
    is_colored: Mapped[bool] = mapped_column(default=False)
    is_large: Mapped[bool] = mapped_column(default=False)
    is_raised: Mapped[bool] = mapped_column(default=False)
    add_phrase: Mapped[bool] = mapped_column(default=False)

    phrase_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    color_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    price_turbo: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    price_color: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    price_large: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    price_raised: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    price_phrase: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="promotion"
    )


class Image(Base):
    """Изображение."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "images"
    id: Mapped[IntPK]
    image_url: Mapped[str] = mapped_column(String)

    announcement_id: Mapped[int] = mapped_column(ForeignKey(ANNOUNCEMENTS_ID_FK))
    position: Mapped[int] = mapped_column(Integer, default=0)

    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="images"
    )
