"""src/schemas/real_estate.py."""

from decimal import Decimal
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from src.models.real_estate import (
    DealStatus,
    RoomCount,
    CommunicationMethod,
    HouseType,
    HouseClass,
    ConstructionTechnology,
    TerritoryType,
    Utilities,
    GasType,
    HeatingType,
    SewerageType,
    WaterSupplyType,
    LayoutType,
    RequestStatus,
)


class ApartmentCreateNested(BaseModel):
    """
    Nested schema for creating an apartment slot.
    """

    number: int


class FloorCreate(BaseModel):
    """Schema for creating a floor."""

    number: int
    apartments: List[ApartmentCreateNested]


class SectionCreate(BaseModel):
    """Schema for creating a section."""

    name: str
    floors: List[FloorCreate]


class HouseInfoBase(BaseModel):
    """Base schema for Housing Complex information (card)."""

    main_image: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    microdistrict: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    house_type: Optional[HouseType] = None
    house_class: Optional[HouseClass] = None
    construction_technology: Optional[ConstructionTechnology] = None
    territory: Optional[TerritoryType] = None
    distance_to_sea: Optional[int] = None
    ceiling_height: Optional[Decimal] = None

    utilities: Optional[Utilities] = None
    gas: Optional[GasType] = None
    heating: Optional[HeatingType] = None
    sewerage: Optional[SewerageType] = None
    water_supply: Optional[WaterSupplyType] = None
    electricity: Optional[bool] = True

    payment_options: Optional[str] = None
    legal_terms: Optional[str] = None


class HouseCreate(BaseModel):
    """Schema for creating a house (Housing Complex)."""

    name: str
    sections: List[SectionCreate]
    info: Optional[HouseInfoBase] = None


class HouseInfoResponse(HouseInfoBase):
    """Schema for Housing Complex information response."""

    id: int
    model_config = ConfigDict(from_attributes=True)


class NewsCreate(BaseModel):
    """Create news."""

    title: str
    description: str
    date: date


class NewsResponse(BaseModel):
    """Schema for Housing Complex news response."""

    id: int
    title: str
    description: str
    date: date
    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(BaseModel):
    """Create document."""

    doc_url: str
    is_excel: bool = False


class DocumentResponse(BaseModel):
    """Schema for Housing Complex document response."""

    id: int
    doc_url: str
    is_excel: bool
    model_config = ConfigDict(from_attributes=True)


class HouseResponse(BaseModel):
    """Schema for house response data."""

    id: int
    name: str
    owner_id: int
    info: Optional[HouseInfoResponse] = None
    news: List[NewsResponse] = []
    documents: List[DocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class HouseInfoUpdate(BaseModel):
    """Schema for editing Housing Complex card."""

    main_image: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    microdistrict: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    house_type: Optional[HouseType] = None
    house_class: Optional[HouseClass] = None
    construction_technology: Optional[ConstructionTechnology] = None
    territory: Optional[TerritoryType] = None
    distance_to_sea: Optional[int] = None
    ceiling_height: Optional[Decimal] = None

    utilities: Optional[Utilities] = None
    gas: Optional[GasType] = None
    heating: Optional[HeatingType] = None
    sewerage: Optional[SewerageType] = None
    water_supply: Optional[WaterSupplyType] = None
    electricity: Optional[bool] = None

    payment_options: Optional[str] = None
    legal_terms: Optional[str] = None


class PromotionCreate(BaseModel):
    """Schema for creating announcement promotion settings."""

    is_turbo: bool = False
    is_colored: bool = False
    is_large: bool = False
    is_raised: bool = False
    add_phrase: bool = False
    phrase_text: Optional[str] = None
    color_type: Optional[str] = None

    price_turbo: Optional[Decimal] = None
    price_color: Optional[Decimal] = None
    price_large: Optional[Decimal] = None
    price_raised: Optional[Decimal] = None
    price_phrase: Optional[Decimal] = None


class PromotionResponse(BaseModel):
    """Schema for promotion response data."""

    id: int
    announcement_id: int
    is_turbo: bool
    is_colored: bool
    is_large: bool
    is_raised: bool
    add_phrase: bool
    phrase_text: Optional[str]
    color_type: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ImageResponse(BaseModel):
    """Schema for image response data."""

    id: int
    image_url: str
    position: int
    model_config = ConfigDict(from_attributes=True)


class ImageUpdateItem(BaseModel):
    """
    Schema for updating an image.
    - id: If provided, means the image already exists, update its position.
    - content: If provided (Base64), means it's a new image.
    """

    id: Optional[int] = Field(
        default=None,
        description="ID of existing image (to keep it and change order).",
    )
    content: Optional[str] = Field(
        default=None,
        description="Base64 string for adding a new image.",
    )


class AnnouncementCreate(BaseModel):
    """Schema for creating an announcement."""

    apartment_id: Optional[int] = None

    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    apartment_number: Optional[str] = None

    price: Decimal
    area: Decimal
    description: str | None = None
    address: str

    house_type: Optional[HouseType] = None
    house_class: Optional[HouseClass] = None
    construction_technology: Optional[ConstructionTechnology] = None
    territory: Optional[TerritoryType] = None
    distance_to_sea: Optional[int] = None
    utilities: Optional[Utilities] = None
    ceiling_height: Optional[Decimal] = None
    gas: Optional[GasType] = None
    heating: Optional[HeatingType] = None
    sewerage: Optional[SewerageType] = None
    water_supply: Optional[WaterSupplyType] = None

    registration: Optional[str] = None
    calculation_options: Optional[str] = None
    purpose: Optional[str] = None
    sum_in_contract: Optional[str] = None
    founding_document: Optional[str] = None

    number_of_rooms: RoomCount = RoomCount.ONE
    layout: Optional[LayoutType] = None
    residential_condition: Optional[str] = None
    kitchen_area: Optional[Decimal] = None
    has_balcony: bool = False

    agent_commission: Decimal = Decimal(0)
    communication_method: CommunicationMethod = CommunicationMethod.ANY

    latitude: Optional[str] = None
    longitude: Optional[str] = None

    images: List[str] = Field(default=[], description="List of images in Base64 format")


class AnnouncementResponse(BaseModel):
    """Schema for response with full announcement data."""

    id: int
    user_id: int
    apartment_id: Optional[int]

    floor_number: Optional[int]
    total_floors: Optional[int]
    apartment_number: Optional[str]

    area: Decimal
    price: Decimal

    description: Optional[str]
    address: str
    status: DealStatus

    house_type: Optional[HouseType]
    house_class: Optional[HouseClass]
    construction_technology: Optional[ConstructionTechnology]
    territory: Optional[TerritoryType]
    distance_to_sea: Optional[int]
    utilities: Optional[Utilities]
    ceiling_height: Optional[Decimal]
    gas: Optional[GasType]
    heating: Optional[HeatingType]
    sewerage: Optional[SewerageType]
    water_supply: Optional[WaterSupplyType]

    registration: Optional[str]
    calculation_options: Optional[str]
    purpose: Optional[str]
    sum_in_contract: Optional[str]
    founding_document: Optional[str]

    number_of_rooms: RoomCount
    layout: Optional[LayoutType]
    residential_condition: Optional[str]
    kitchen_area: Optional[Decimal]
    has_balcony: bool

    agent_commission: Optional[Decimal]
    communication_method: CommunicationMethod
    rejection_reason: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]

    created_at: datetime
    updated_at: datetime

    images: List[ImageResponse] = []
    promotion: Optional[PromotionResponse] = None

    model_config = ConfigDict(from_attributes=True)


class AnnouncementUpdate(BaseModel):
    """
    Schema for updating an announcement.
    """

    price: Optional[Decimal] = None
    area: Optional[Decimal] = None
    description: Optional[str] = None
    address: Optional[str] = None
    status: Optional[DealStatus] = None

    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    apartment_number: Optional[str] = None

    house_type: Optional[HouseType] = None
    house_class: Optional[HouseClass] = None
    construction_technology: Optional[ConstructionTechnology] = None
    territory: Optional[TerritoryType] = None
    distance_to_sea: Optional[int] = None
    utilities: Optional[Utilities] = None
    ceiling_height: Optional[Decimal] = None
    gas: Optional[GasType] = None
    heating: Optional[HeatingType] = None
    sewerage: Optional[SewerageType] = None
    water_supply: Optional[WaterSupplyType] = None

    registration: Optional[str] = None
    calculation_options: Optional[str] = None
    purpose: Optional[str] = None
    sum_in_contract: Optional[str] = None
    founding_document: Optional[str] = None

    number_of_rooms: Optional[RoomCount] = None
    layout: Optional[LayoutType] = None
    residential_condition: Optional[str] = None
    kitchen_area: Optional[Decimal] = None
    has_balcony: Optional[bool] = None

    agent_commission: Optional[Decimal] = None
    communication_method: Optional[CommunicationMethod] = None
    rejection_reason: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    images: Optional[List[ImageUpdateItem]] = None


class PromotionUpdate(BaseModel):
    """
    Schema for updating promotion.
    """

    is_turbo: Optional[bool] = None
    is_colored: Optional[bool] = None
    is_large: Optional[bool] = None
    is_raised: Optional[bool] = None
    add_phrase: Optional[bool] = None
    phrase_text: Optional[str] = None
    color_type: Optional[str] = None

    price_turbo: Optional[Decimal] = None
    price_color: Optional[Decimal] = None
    price_large: Optional[Decimal] = None
    price_raised: Optional[Decimal] = None
    price_phrase: Optional[Decimal] = None


class AnnouncementReject(BaseModel):
    """Schema for rejecting an announcement."""

    reason: str


class ChessboardRequestCreate(BaseModel):
    """Create request to add to chessboard."""

    target_house_id: int
    target_section_id: int
    target_floor_id: int
    target_apartment_number: int


class ChessboardRequestResponse(BaseModel):
    """Request response."""

    id: int
    announcement_id: int
    target_house_id: int
    status: RequestStatus
    developer_comment: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResolveRequestSchema(BaseModel):
    """Schema for deciding on a request (approve/reject)."""

    approved: bool
    comment: str | None = None


class AnnouncementFilter(BaseModel):
    """
    Filter for searching announcements.
    """

    type_secondary: bool = False
    type_new_buildings: bool = False
    type_cottage: bool = False

    status_house: Optional[DealStatus] = None

    district: Optional[str] = None  # Search by substring in address
    microdistrict: Optional[str] = None  # Search by substring in address

    price_from: Optional[Decimal] = None
    price_to: Optional[Decimal] = None
    area_from: Optional[Decimal] = None
    area_to: Optional[Decimal] = None

    purpose: Optional[str] = None
    purchase_terms: Optional[str] = None
    condition: Optional[str] = None
    number_of_rooms: Optional[RoomCount] = None
    house_type: Optional[HouseType] = None
    house_class: Optional[HouseClass] = None
    has_balcony: Optional[bool] = None
