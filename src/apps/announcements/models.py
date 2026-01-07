"""src/apps/announcements/models.py."""

from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.orderinglist import ordering_list
from src.apps.users.models import Favorite
from src.core.enum import (
    DealStatus,
    HouseType,
    ConstructionTechnology,
    HouseClass,
    TerritoryType,
    Utilities,
    WaterSupplyType,
    GasType,
    HeatingType,
    SewerageType,
    LayoutType,
    RoomCount,
    CommunicationMethod,
    RequestStatus,
)
from src.core.models.base import Base, IntPK, CreatedAt, UpdatedAt


if TYPE_CHECKING:
    from src.apps.users.models import User
    from src.apps.buildings.models import Apartment, House, News, Document

CASCADE_ALL_DELETE = "all, delete-orphan"
ANNOUNCEMENTS_ID_FK = "announcements.id"
HOUSES_ID_FK = "houses.id"


class Announcement(Base):
    """Sales announcement."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "announcements"

    id: Mapped[IntPK]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    apartment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("apartments.id"), unique=True, nullable=True
    )

    floor_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    apartment_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    area: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2))
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
    favorited_by: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="announcement"
    )
    chessboard_request: Mapped[Optional["ChessboardRequest"]] = relationship(
        "ChessboardRequest",
        back_populates="announcement",
        uselist=False,
        cascade=CASCADE_ALL_DELETE,
    )


class ChessboardRequest(Base):
    """
    Chessboard linking request (linking announcement to a house apartment).
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
    house: Mapped["House"] = relationship("House", back_populates="chessboard_requests")


class Promotion(Base):
    """Paid promotion."""

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
    """Image."""

    # pylint: disable=too-few-public-methods
    __tablename__ = "images"
    id: Mapped[IntPK]
    image_url: Mapped[str] = mapped_column(String)

    announcement_id: Mapped[int] = mapped_column(ForeignKey(ANNOUNCEMENTS_ID_FK))
    position: Mapped[int] = mapped_column(Integer, default=0)

    announcement: Mapped["Announcement"] = relationship(
        "Announcement", back_populates="images"
    )
