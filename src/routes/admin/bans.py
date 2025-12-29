"""src/routes/admin/bans.py."""

from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.common.exceptions import (
    PermissionDeniedError,
    ResourceNotFoundError,
    AuthenticationFailedError,
)
from src.models import User
from src.routes.deps import get_current_user
from src.services.admin import AdminService

router = APIRouter(tags=["Ban/Unban User"])


@router.post(
    "/users/{user_id}/ban",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def ban_user(
    user_id: int,
    service: FromDishka[AdminService],
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
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """
    Unban a user.
    (Moderator only).
    """
    return await service.unban_user(current_user, user_id)
