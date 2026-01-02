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
    Extracts token, validates it, and returns the user.
    Also checks if the user is banned.
    """
    token = token_creds.credentials

    user = await auth_service.get_current_user(token)

    is_banned = await user_repo.is_user_banned(user.id)
    if is_banned:
        logger.warning("Banned user %s tried to access API", user.id)
        raise PermissionDeniedError()

    return user
