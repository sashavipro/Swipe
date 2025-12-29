"""src/routes/auth.py."""

import logging

from fastapi import APIRouter, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.common.exceptions import (
    ResourceAlreadyExistsError,
    AuthenticationFailedError,
    ResourceNotFoundError,
    BadRequestError,
)
from src.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    RefreshTokenRequest,
    ResetPasswordRequest,
    ForgotPasswordRequest,
    UserVerification,
)
from src.services.auth import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_200_OK,
    responses=create_error_responses(ResourceAlreadyExistsError, BadRequestError),
)
@inject
async def register(
    service: FromDishka[AuthService],
    data: UserRegister,
):
    """
    Step 1. Initiate registration.
    Sends verification code to email. Data is stored temporarily.
    """
    return await service.register_user(data)


@router.post(
    "/verify",
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, ResourceAlreadyExistsError
    ),
)
@inject
async def verify_registration(
    service: FromDishka[AuthService],
    data: UserVerification,
):
    """
    Step 2. Complete registration.
    Verifies code and creates user in database.
    """
    return await service.verify_registration(data.email, data.code)


@router.post(
    "/login",
    response_model=Token,
    responses=create_error_responses(AuthenticationFailedError),
)
@inject
async def login(
    service: FromDishka[AuthService],
    data: UserLogin,
):
    """
    Log in to the system. Returns Access and Refresh tokens.
    """
    return await service.authenticate_user(data)


@router.post(
    "/refresh",
    response_model=Token,
    responses=create_error_responses(AuthenticationFailedError),
)
@inject
async def refresh_tokens(service: FromDishka[AuthService], data: RefreshTokenRequest):
    """
    Refresh tokens using a valid Refresh Token.
    """
    return await service.refresh_token(data.refresh_token)


@router.post("/forgot-password")
@inject
async def forgot_password(
    service: FromDishka[AuthService], data: ForgotPasswordRequest
):
    """Request password reset."""
    return await service.request_password_reset(data.email)


@router.post(
    "/reset-password",
    responses=create_error_responses(
        AuthenticationFailedError, ResourceNotFoundError, BadRequestError
    ),
)
@inject
async def reset_password(service: FromDishka[AuthService], data: ResetPasswordRequest):
    """Reset password using a token."""
    return await service.reset_password(data)
