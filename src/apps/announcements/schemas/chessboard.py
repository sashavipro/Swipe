"""src/apps/announcements/schemas/chessboard.py."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.core.enum import RequestStatus


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
