"""src/apps/buildings/schemas.py."""

from decimal import Decimal
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, ConfigDict
from src.core.enum import (
    HouseType,
    HouseClass,
    ConstructionTechnology,
    TerritoryType,
    Utilities,
    GasType,
    HeatingType,
    SewerageType,
    WaterSupplyType,
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


class ApartmentResponse(BaseModel):
    """Schema for apartment response data."""

    id: int
    number: int
    model_config = ConfigDict(from_attributes=True)


class FloorResponse(BaseModel):
    """Schema for floor response data."""

    id: int
    number: int
    apartments: List[ApartmentResponse] = []
    model_config = ConfigDict(from_attributes=True)


class SectionResponse(BaseModel):
    """Schema for section response data."""

    id: int
    name: str
    floors: List[FloorResponse] = []
    model_config = ConfigDict(from_attributes=True)


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


class NewsResponse(BaseModel):
    """Schema for Housing Complex news response."""

    id: int
    title: str
    description: str
    date: date
    model_config = ConfigDict(from_attributes=True)


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
    sections: List[SectionResponse] = []

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


class NewsCreate(BaseModel):
    """Create news."""

    title: str
    description: str
    date: date


class DocumentCreate(BaseModel):
    """Create document."""

    doc_url: str
    is_excel: bool = False
