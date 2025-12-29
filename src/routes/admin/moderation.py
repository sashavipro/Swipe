"""src/routes/admin/moderation.py."""

from typing import List
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
from src.schemas.real_estate import AnnouncementResponse, AnnouncementReject
from src.services.admin import AdminService

router = APIRouter(tags=["Announcement Moderation"])


@router.get(
    "/announcements/pending",
    response_model=List[AnnouncementResponse],
    responses=create_error_responses(AuthenticationFailedError, PermissionDeniedError),
)
@inject
async def get_pending_announcements(
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """
    Get list of announcements pending moderation.
    (Moderator only).
    """
    return await service.get_pending_announcements(current_user)


@router.post(
    "/announcements/{announcement_id}/approve",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def approve_announcement(
    announcement_id: int,
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """
    Approve announcement (set status to ACTIVE).
    """
    return await service.approve_announcement(current_user, announcement_id)


@router.post(
    "/announcements/{announcement_id}/reject",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def reject_announcement(
    announcement_id: int,
    data: AnnouncementReject,
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """
    Reject announcement (with reason).
    """
    return await service.reject_announcement(current_user, announcement_id, data)
