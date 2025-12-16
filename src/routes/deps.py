"""src/routes/deps.py."""

from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject

from src.services.auth import AuthService
from src.models.users import User

security = HTTPBearer()


@inject
async def get_current_user(
    token_creds: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: FromDishka[AuthService],
) -> User:
    """
    Достает токен, проверяет его и возвращает юзера.
    """
    token = token_creds.credentials

    return await auth_service.get_current_user(token)
