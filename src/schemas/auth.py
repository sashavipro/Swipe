"""src/schemas/auth.py."""

# pylint: disable=duplicate-code
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Схема для регистрации нового пользователя."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    first_name: str
    last_name: str
    phone: str


class UserLogin(BaseModel):
    """Схема для входа в систему."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Модель ответа с токенами."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена."""

    refresh_token: str


class UserResponse(BaseModel):
    """Публичный профиль пользователя."""

    id: int
    email: str
    first_name: str
    last_name: str

    class Config:
        """Конфигурация Pydantic."""

        # pylint: disable=too-few-public-methods
        from_attributes = True
