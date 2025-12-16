"""src/routes/auth.py."""

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from src.schemas.auth import UserRegister, UserLogin, Token, RefreshTokenRequest
from src.services.auth import AuthService

router = APIRouter(tags=["Auth"])


@router.post("/register")
@inject
async def register(
    service: FromDishka[AuthService],
    data: UserRegister,
):
    """
    Регистрация нового пользователя.
    """
    return await service.register_user(data)


@router.post("/login", response_model=Token)
@inject
async def login(
    service: FromDishka[AuthService],
    data: UserLogin,
):
    """
    Вход в систему. Возвращает Access и Refresh токены.
    """
    return await service.authenticate_user(data)


@router.post("/refresh", response_model=Token)
@inject
async def refresh_tokens(service: FromDishka[AuthService], data: RefreshTokenRequest):
    """
    Принимает старый Refresh Token, возвращает новую пару (Access + Refresh).
    """
    return await service.refresh_token(data.refresh_token)
