"""src/apps/users/schemas/complaint.py."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.apps.users.models import ComplaintReason


class ComplaintCreate(BaseModel):
    """Create complaint."""

    reported_user_id: int
    reason: ComplaintReason
    description: Optional[str] = None


class ComplaintResponse(BaseModel):
    """View complaint."""

    id: int
    reporter_id: int
    reported_user_id: int
    reason: ComplaintReason
    description: Optional[str]
    is_resolved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
