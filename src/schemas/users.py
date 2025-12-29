"""src/schemas/users.py."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.common.schemas import PhoneSchemaMixin
from src.models.users import UserRole, NotificationType, ComplaintReason


class UserCreateBase(PhoneSchemaMixin, BaseModel):
    """Base schema for user creation."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    first_name: str
    last_name: str
    phone: str


class UserRegister(UserCreateBase):
    """Schema for public registration."""


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


class SubscriptionResponse(BaseModel):
    """Subscription information."""

    id: int
    paid_to: date
    auto_renewal: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdateByAdmin(UserUpdate):
    """Schema for updating user by admin (allows role change)."""

    role: Optional[UserRole] = None


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


class DeveloperCreate(UserCreateBase):
    """Schema for creating a Developer."""


class NotaryCreate(UserCreateBase):
    """Schema for creating a Notary."""


class AgentCreate(UserCreateBase):
    """Schema for creating an Agent."""


class ModeratorCreate(UserCreateBase):
    """Schema for creating a Moderator."""


class SimpleUserCreate(UserCreateBase):
    """Schema for creating a simple user (via admin)."""
