import enum
from typing import List, Optional, TYPE_CHECKING
from datetime import date

from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Float, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, int_pk, created_at, updated_at

if TYPE_CHECKING:
    from src.models.users import User, Chosen


class DealStatus(str, enum.Enum):
    ACTIVE = "active"
    SOLD = "sold"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class HouseType(str, enum.Enum):
    MONOLITHIC = "monolithic"
    PANEL = "panel"
    BRICK = "brick"
    BLOCK = "block"


class HouseClass(str, enum.Enum):
    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    ELITE = "elite"


class ConstructionTechnology(str, enum.Enum):
    MONOLITH = "monolith"
    BRICK = "brick"


class TerritoryType(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"


class Utilities(str, enum.Enum):
    CENTRAL = "central"
    AUTONOMOUS = "autonomous"


class GasType(str, enum.Enum):
    MAIN = "main"
    NONE = "none"


class HeatingType(str, enum.Enum):
    CENTRAL = "central"
    GAS = "gas"
    ELECTRIC = "electric"


class SewerageType(str, enum.Enum):
    CENTRAL = "central"
    SEPTIC = "septic"


class WaterSupplyType(str, enum.Enum):
    CENTRAL = "central"
    WELL = "well"


class LayoutType(str, enum.Enum):
    ISOLATED = "isolated"
    ADJACENT = "adjacent"
    STUDIO = "studio"


class RoomCount(str, enum.Enum):
    STUDIO = "studio"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR_PLUS = "4+"


class CommunicationMethod(str, enum.Enum):
    CALL = "call"
    MESSAGE = "message"
    ANY = "any"


class News(Base):
    __tablename__ = "news"

    id: Mapped[int_pk]
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)

    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="news"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int_pk]
    is_excel: Mapped[bool] = mapped_column(Boolean, default=False)
    doc_url: Mapped[str] = mapped_column(String)

    announcements: Mapped[List["Announcement"]] = relationship(
        "Announcement", back_populates="document"
    )


class House(Base):
    __tablename__ = "houses"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String)

    sections: Mapped[List["Section"]] = relationship(
        "Section", back_populates="house", cascade="all, delete-orphan"
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int_pk]
    house_id: Mapped[int] = mapped_column(ForeignKey("houses.id"))
    number: Mapped[int] = mapped_column(Integer)

    house: Mapped["House"] = relationship("House", back_populates="sections")
    floors: Mapped[List["Floor"]] = relationship(
        "Floor", back_populates="section", cascade="all, delete-orphan"
    )


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[int_pk]
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    number: Mapped[int] = mapped_column(Integer)

    section: Mapped["Section"] = relationship("Section", back_populates="floors")
    apartments: Mapped[List["Apartment"]] = relationship(
        "Apartment", back_populates="floor"
    )


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int_pk]

    # Владелец (User)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    news_id: Mapped[Optional[int]] = mapped_column(ForeignKey("news.id"), nullable=True)
    document_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )

    description: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[str] = mapped_column(String)  # adres

    status: Mapped[DealStatus] = mapped_column(default=DealStatus.ACTIVE)
    house_type: Mapped[Optional[HouseType]] = mapped_column(nullable=True)
    house_class: Mapped[Optional[HouseClass]] = mapped_column(
        nullable=True
    )  # class_at_home
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

    area: Mapped[float] = mapped_column(Float)
    kitchen_area: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    has_balcony: Mapped[bool] = mapped_column(default=False)  # balcony_or_loggia

    price: Mapped[float] = mapped_column(Float)
    agent_commission: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    communication_method: Mapped[CommunicationMethod] = mapped_column(
        default=CommunicationMethod.ANY
    )

    # Модерация
    rejection_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    latitude: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    # Владелец
    owner: Mapped["User"] = relationship("User", back_populates="announcements")

    news: Mapped[Optional["News"]] = relationship(
        "News", back_populates="announcements"
    )
    document: Mapped[Optional["Document"]] = relationship(
        "Document", back_populates="announcements"
    )

    images: Mapped[List["Image"]] = relationship(
        "Image", back_populates="announcement", cascade="all, delete-orphan"
    )
    promotion: Mapped[Optional["Promotion"]] = relationship(
        "Promotion",
        back_populates="announcement",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Связь с физической квартирой
    apartment_unit: Mapped[Optional["Apartment"]] = relationship(
        "Apartment", back_populates="announcement", uselist=False
    )

    # Обратная связь к избранному (Defined in users.py)
    favorited_by: Mapped[List["Chosen"]] = relationship(
        "Chosen", back_populates="announcement"
    )


class Apartment(Base):
    """
    Физическая привязка объявления к дому/этажу.
    По схеме: ссылается на Floor и на Announcement.
    """

    __tablename__ = "apartments"

    id: Mapped[int_pk]
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))
    announcement_id: Mapped[int] = mapped_column(ForeignKey("announcements.id"))

    number_on_floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    floor: Mapped["Floor"] = relationship("Floor", back_populates="apartments")
    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="apartment_unit"
    )


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int_pk]
    announcement_id: Mapped[int] = mapped_column(ForeignKey("announcements.id"))
    image_url: Mapped[str] = mapped_column(String)

    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="images"
    )


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int_pk]
    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id"), unique=True
    )

    is_colored: Mapped[bool] = mapped_column(default=False)
    color_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    is_large: Mapped[bool] = mapped_column(default=False)  # large_advertisement
    is_raised: Mapped[bool] = mapped_column(default=False)  # raise_advertisement
    is_turbo: Mapped[bool] = mapped_column(default=False)

    add_phrase: Mapped[bool] = mapped_column(default=False)
    phrase_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    price_phrase: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_color: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_large: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_raised: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_turbo: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="promotion"
    )
