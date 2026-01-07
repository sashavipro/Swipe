"""src/apps/admin/routers/blacklist.py."""

from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.admin.services.blacklist import BlacklistService
from src.apps.users.models import User
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceNotFoundError,
)

router = APIRouter(prefix="/admin", tags=["Ban/Unban User"])


@router.post(
    "/users/{user_id}/ban",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def ban_user(
    user_id: int,
    service: FromDishka[BlacklistService],
    current_user: User = Depends(get_current_user),
):
    """
    Ban a user.
    (Moderator only).
    """
    return await service.ban_user(current_user, user_id)


@router.post(
    "/users/{user_id}/unban",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def unban_user(
    user_id: int,
    service: FromDishka[BlacklistService],
    current_user: User = Depends(get_current_user),
):
    """
    Unban a user.
    (Moderator only).
    """
    return await service.unban_user(current_user, user_id)
