"""src/apps/users/schemas/saved_searches.py."""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.apps.users.models import PropertyType
from src.core.enum import ConstructionStatus, PurchaseTerms, Purpose, Condition


class SavedSearchBase(BaseModel):
    """Base filter schema."""

    type_secondary: bool = False
    type_new_buildings: bool = False
    type_cottage: bool = False

    type_of_property: Optional[PropertyType] = None
    status_house: Optional[ConstructionStatus] = None
    district: Optional[str] = None
    microdistrict: Optional[str] = None
    number_of_rooms: Optional[int] = None

    price_from: Optional[Decimal] = None
    price_to: Optional[Decimal] = None
    area_from: Optional[Decimal] = None
    area_to: Optional[Decimal] = None

    purpose: Optional[Purpose] = None
    purchase_terms: Optional[PurchaseTerms] = None
    condition: Optional[Condition] = None


class SavedSearchCreate(SavedSearchBase):
    """Schema for creating a saved search."""


class SavedSearchResponse(SavedSearchBase):
    """Response schema."""

    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
