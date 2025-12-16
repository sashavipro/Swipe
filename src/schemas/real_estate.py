"""src/schemas/real_estate.py."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
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
)


class ApartmentCreateNested(BaseModel):
    """
    Вложенная схема для создания слота квартиры.
    Используется внутри FloorCreate.
    """


class FloorCreate(BaseModel):
    """Схема для создания этажа."""

    number: int
    apartments: List[ApartmentCreateNested]


class SectionCreate(BaseModel):
    """Схема для создания секции (подъезда)."""

    name: str
    floors: List[FloorCreate]


class HouseCreate(BaseModel):
    """Схема для создания дома (ЖК)."""

    name: str
    sections: List[SectionCreate]


class HouseResponse(BaseModel):
    """Схема ответа с данными о доме."""

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class PromotionCreate(BaseModel):
    """Схема для создания настроек продвижения объявления."""

    is_turbo: bool = False
    is_colored: bool = False
    is_large: bool = False
    is_raised: bool = False
    add_phrase: bool = False
    phrase_text: Optional[str] = None
    color_type: Optional[str] = None

    price_turbo: Optional[float] = None
    price_color: Optional[float] = None
    price_large: Optional[float] = None
    price_raised: Optional[float] = None
    price_phrase: Optional[float] = None


class PromotionResponse(BaseModel):
    """Схема ответа с данными о продвижении."""

    id: int
    is_turbo: bool
    is_colored: bool
    is_large: bool
    is_raised: bool
    add_phrase: bool
    phrase_text: Optional[str]
    color_type: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ImageResponse(BaseModel):
    """Схема ответа с данными об изображении."""

    id: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class AnnouncementCreate(BaseModel):
    """Схема для создания объявления."""

    apartment_id: int

    apartment_number: int
    price: float
    total_area: float
    description: str | None = None
    address: str

    house_type: Optional[HouseType] = None
    house_class: Optional[HouseClass] = None
    construction_technology: Optional[ConstructionTechnology] = None
    territory: Optional[TerritoryType] = None
    distance_to_sea: Optional[int] = None
    utilities: Optional[Utilities] = None
    ceiling_height: Optional[float] = None
    gas: Optional[GasType] = None
    heating: Optional[HeatingType] = None
    sewerage: Optional[SewerageType] = None
    water_supply: Optional[WaterSupplyType] = None

    registration: Optional[str] = None
    calculation_options: Optional[str] = None
    purpose: Optional[str] = None
    sum_in_contract: Optional[str] = None
    founding_document: Optional[str] = None

    rooms: RoomCount = RoomCount.ONE
    layout: Optional[LayoutType] = None
    residential_condition: Optional[str] = None
    kitchen_area: Optional[float] = None
    has_balcony: bool = False

    agent_commission: float = 0.0
    communication_method: CommunicationMethod = CommunicationMethod.ANY

    latitude: Optional[str] = None
    longitude: Optional[str] = None

    image_ids: List[int] = []
    promotion: Optional[PromotionCreate] = None


class AnnouncementResponse(BaseModel):
    """Схема ответа с полными данными об объявлении."""

    id: int
    user_id: int
    apartment_id: int

    apartment_number: int
    area: float
    price: float

    description: Optional[str]
    address: str
    status: DealStatus

    house_type: Optional[HouseType]
    house_class: Optional[HouseClass]
    construction_technology: Optional[ConstructionTechnology]
    territory: Optional[TerritoryType]
    distance_to_sea: Optional[int]
    utilities: Optional[Utilities]
    ceiling_height: Optional[float]
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
    kitchen_area: Optional[float]
    has_balcony: bool

    agent_commission: Optional[float]
    communication_method: CommunicationMethod
    rejection_reason: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]

    created_at: datetime
    updated_at: datetime

    # Вложенные объекты
    images: List[ImageResponse] = []
    promotion: Optional[PromotionResponse] = None

    model_config = ConfigDict(from_attributes=True)
