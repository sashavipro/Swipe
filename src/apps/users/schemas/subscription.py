"""src/apps/users/schemas/subscription.py."""

from datetime import date
from pydantic import BaseModel, ConfigDict


class SubscriptionResponse(BaseModel):
    """Subscription information."""

    id: int
    paid_to: date
    auto_renewal: bool

    model_config = ConfigDict(from_attributes=True)
