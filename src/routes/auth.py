"""src/routes/auth.py."""

import logging

from fastapi import APIRouter, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    RefreshTokenRequest,
    VerificationTokenResponse,
    EmailVerificationRequest,
    EmailVerificationCheck,
    ResetPasswordRequest,
    ForgotPasswordRequest,
)
from src.services.auth import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Auth"])


@router.post(
    "/send-code",
    status_code=status.HTTP_200_OK,
    responses=create_error_responses(409, 422),
)
@inject
async def send_verification_code(
    service: FromDishka[AuthService],
    data: EmailVerificationRequest,
):
    """
    Шаг 1. Отправить код верификации на Email.
    """
    return await service.send_verification_code(data.email)


@router.post(
    "/verify-code",
    response_model=VerificationTokenResponse,
    status_code=status.HTTP_200_OK,
    responses=create_error_responses(401, 422),
)
@inject
async def verify_code(
    service: FromDishka[AuthService],
    data: EmailVerificationCheck,
):
    """
    Шаг 2. Проверить полученный Email код.
    """
    return await service.verify_email_code(data.email, data.code)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(401, 403, 409, 422),
)
@inject
async def register(
    service: FromDishka[AuthService],
    data: UserRegister,
):
    """
    Шаг 3. Регистрация (требует verification_token от Шага 2).
    """
    return await service.register_user(data)


@router.post("/login", response_model=Token, responses=create_error_responses(401, 422))
@inject
async def login(
    service: FromDishka[AuthService],
    data: UserLogin,
):
    """
    Вход в систему. Возвращает Access и Refresh токены.
    - **401**: Неверный логин или пароль.
    """
    return await service.authenticate_user(data)


@router.post(
    "/refresh", response_model=Token, responses=create_error_responses(401, 422)
)
@inject
async def refresh_tokens(service: FromDishka[AuthService], data: RefreshTokenRequest):
    """
    Принимает старый Refresh Token, возвращает новую пару (Access + Refresh).
    - **401**: Токен невалиден или просрочен.
    """
    return await service.refresh_token(data.refresh_token)


@router.post("/forgot-password")
@inject
async def forgot_password(
    service: FromDishka[AuthService], data: ForgotPasswordRequest
):
    """Запрос на восстановление пароля."""
    return await service.request_password_reset(data.email)


@router.post("/reset-password")
@inject
async def reset_password(service: FromDishka[AuthService], data: ResetPasswordRequest):
    """Сброс пароля с использованием токена."""
    return await service.reset_password(data)
