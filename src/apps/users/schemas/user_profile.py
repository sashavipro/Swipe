"""src/apps/users/schemas/user_profile.py."""

from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from src.apps.auth.schemas import UserCreateBase
from src.apps.users.models import UserRole, NotificationType
from src.core.schemas.mixin import PhoneSchemaMixin


class EmployeeCreate(UserCreateBase):
    """Schema for creating an employee with a role."""

    role: UserRole = UserRole.AGENT


class AgentContactSchema(PhoneSchemaMixin, BaseModel):
    """Agent contact schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(PhoneSchemaMixin, BaseModel):
    """Schema for updating profile data."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    notification_type: Optional[NotificationType] = None
    notification_transfer: Optional[bool] = None

    agent_contact: Optional[AgentContactSchema] = None


class UserResponse(BaseModel):
    """Schema for user data response."""

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    role: UserRole
    avatar: Optional[str] = None
    agent_contact: Optional[AgentContactSchema] = None

    model_config = ConfigDict(from_attributes=True)
