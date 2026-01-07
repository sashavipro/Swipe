"""src/apps/admin/schemas.py."""

from typing import Optional

from src.apps.auth.schemas import UserCreateBase
from src.apps.users.schemas.user_profile import UserUpdate
from src.core.enum import UserRole


class UserUpdateByAdmin(UserUpdate):
    """Schema for updating user by admin (allows role change)."""

    role: Optional[UserRole] = None


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
