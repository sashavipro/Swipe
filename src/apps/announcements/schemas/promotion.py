"""src/apps/announcements/schemas/promotion.py."""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


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
