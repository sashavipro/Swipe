"""src/apps/buildings/models.py"""

from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from sqlalchemy import ForeignKey, String, Date, Boolean, Text, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models.base import Base, IntPK
from src.core.enum import (
    HouseType,
    ConstructionTechnology,
    HouseClass,
    TerritoryType,
    Utilities,
    GasType,
    SewerageType,
    HeatingType,
    WaterSupplyType,
)

if TYPE_CHECKING:
    from src.apps.users.models import User
    from src.apps.announcements.models import Announcement, ChessboardRequest


CASCADE_ALL_DELETE = "all, delete-orphan"
ANNOUNCEMENTS_ID_FK = "announcements.id"
HOUSES_ID_FK = "houses.id"


class News(Base):
    """Housing complex news."""

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
    """Housing complex documents."""

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
    Detailed information about the Housing Complex (Housing Complex Card).
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
    """Housing Complex (House)."""

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
    chessboard_requests: Mapped[List["ChessboardRequest"]] = relationship(
        "ChessboardRequest", back_populates="house", cascade=CASCADE_ALL_DELETE
    )


class Section(Base):
    """Section (Entrance)."""

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
    """Floor."""

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
    Physical apartment (Chessboard cell).
    """

    # pylint: disable=too-few-public-methods
    __tablename__ = "apartments"

    id: Mapped[IntPK]
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))

    number: Mapped[int] = mapped_column(Integer)

    floor: Mapped["Floor"] = relationship("Floor", back_populates="apartments")

    announcement: Mapped[Optional["Announcement"]] = relationship(
        "Announcement",
        back_populates="apartment_unit",
        uselist=False,
    )
