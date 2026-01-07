"""src/apps/users/schemas/chat.py."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    """
    Schema for creating a new message.
    """

    recipient_id: int
    content: Optional[str] = None
    file_url: Optional[str] = None


class MessageResponse(BaseModel):
    """
    Schema for message response data.
    """

    id: int
    sender_id: int
    recipient_id: int
    content: Optional[str]
    file_url: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
