"""src/routes/deps.py."""

import logging
from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject

from src.common.exceptions import PermissionDeniedError
from src.repositories.users import UserRepository
from src.services.auth import AuthService
from src.models.users import User

logger = logging.getLogger(__name__)
security = HTTPBearer()


@inject
async def get_current_user(
    token_creds: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: FromDishka[AuthService],
    user_repo: FromDishka[UserRepository],
) -> User:
    """
    Достает токен, проверяет его и возвращает юзера.
    Также проверяет, не забанен ли пользователь.
    """
    token = token_creds.credentials

    # Аутентификация (auth_service сам кинет AuthenticationFailedError если что не так)
    user = await auth_service.get_current_user(token)

    # Авторизация (проверка бана)
    is_banned = await user_repo.is_user_banned(user.id)
    if is_banned:
        logger.warning("Banned user %s tried to access API", user.id)
        raise PermissionDeniedError("Your account has been banned. Access denied.")

    return user
