"""src/schemas/users.py."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.models.users import UserRole, NotificationType


class UserCreateBase(BaseModel):
    """Базовая схема создания пользователя."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    first_name: str
    last_name: str
    phone: str


class UserRegister(UserCreateBase):
    """Схема для публичной регистрации."""


class EmployeeCreate(UserCreateBase):
    """Схема для создания сотрудника с указанием роли."""

    role: UserRole = UserRole.AGENT


class AgentContactSchema(BaseModel):
    """Схема контактов агента."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Схема для обновления данных профиля."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    notification_type: Optional[NotificationType] = None
    notification_transfer: Optional[bool] = None

    agent_contact: Optional[AgentContactSchema] = None


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""

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
    """Информация о подписке."""

    id: int
    paid_to: date
    auto_renewal: bool

    model_config = ConfigDict(from_attributes=True)
