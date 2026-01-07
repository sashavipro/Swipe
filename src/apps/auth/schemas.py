"""src/apps/auth/schemas.py."""

from pydantic import BaseModel, EmailStr, Field

from src.core.schemas.mixin import PhoneSchemaMixin


class UserCreateBase(PhoneSchemaMixin, BaseModel):
    """Base schema for user creation."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    first_name: str
    last_name: str
    phone: str


class EmailVerificationRequest(BaseModel):
    """Request to send verification code to Email."""

    email: EmailStr


class VerificationTokenResponse(BaseModel):
    """Response after successful code verification."""

    verification_token: str
    message: str


class UserRegister(UserCreateBase):
    """
    Schema for new user registration.
    Inherits fields (email, password, name, phone) from UserCreateBase.
    """

    # No extra fields needed now


class UserVerification(BaseModel):
    """
    Schema for finalizing registration.
    """

    email: EmailStr
    code: str = Field(min_length=4, max_length=6)


class UserLogin(BaseModel):
    """Schema for system login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request to refresh token."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Set new password."""

    token: str
    new_password: str = Field(min_length=6, max_length=100)
