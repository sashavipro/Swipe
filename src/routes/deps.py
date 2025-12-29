"""src/routes/deps.py."""

import logging
from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject

from src.common.exceptions import PermissionDeniedError
from src.repositories.users import UserRepository
from src.services.announcements import AnnouncementService
from src.services.auth import AuthService
from src.models.users import User
from src.services.saved_searches import SavedSearchService

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


class SearchDependencies:
    """
    Dependency wrapper for search services.
    Used to group arguments and avoid 'too-many-arguments' linter error.
    """

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        saved_search_service: FromDishka[SavedSearchService],
        announcement_service: FromDishka[AnnouncementService],
        user: User = Depends(get_current_user),
    ):
        self.saved_search_service = saved_search_service
        self.announcement_service = announcement_service
        self.user = user
