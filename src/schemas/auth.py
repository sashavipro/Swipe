"""src/schemas/auth.py."""

from pydantic import BaseModel, EmailStr, Field

from src.schemas.users import UserCreateBase


class EmailVerificationRequest(BaseModel):
    """Запрос на отправку кода на Email."""

    email: EmailStr


class EmailVerificationCheck(BaseModel):
    """Проверка Email кода."""

    email: EmailStr
    code: str = Field(min_length=4, max_length=6)


class VerificationTokenResponse(BaseModel):
    """Ответ после успешной проверки кода."""

    verification_token: str
    message: str


class UserRegister(UserCreateBase):
    """
    Схема для регистрации нового пользователя.
    Наследует поля (email, password, name, phone) от UserCreateBase.
    Добавляет verification_token.
    """

    verification_token: str


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


class ForgotPasswordRequest(BaseModel):
    """Запрос на сброс пароля."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Установка нового пароля."""

    token: str
    new_password: str = Field(min_length=6, max_length=100)
