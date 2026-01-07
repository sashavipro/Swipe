"""src/apps/admin/routers/admin/moderation_announcement.py."""

from typing import List
from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.admin.services.moderation_announcement import (
    ModerationAnnouncementService,
)
from src.apps.announcements.schemas.announcement import (
    AnnouncementResponse,
    AnnouncementReject,
)
from src.apps.users.models import User
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceNotFoundError,
)

router = APIRouter(prefix="/admin", tags=["Announcement Moderation"])


@router.get(
    "/announcement/pending",
    response_model=List[AnnouncementResponse],
    responses=create_error_responses(AuthenticationFailedError, PermissionDeniedError),
)
@inject
async def get_pending_announcements(
    service: FromDishka[ModerationAnnouncementService],
    current_user: User = Depends(get_current_user),
):
    """
    Get list of announcements pending moderation.
    (Moderator only).
    """
    return await service.get_pending_announcements(current_user)


@router.post(
    "/announcement/{announcement_id}/approve",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def approve_announcement(
    announcement_id: int,
    service: FromDishka[ModerationAnnouncementService],
    current_user: User = Depends(get_current_user),
):
    """
    Approve announcement (set status to ACTIVE).
    """
    return await service.approve_announcement(current_user, announcement_id)


@router.post(
    "/announcement/{announcement_id}/reject",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def reject_announcement(
    announcement_id: int,
    data: AnnouncementReject,
    service: FromDishka[ModerationAnnouncementService],
    current_user: User = Depends(get_current_user),
):
    """
    Reject announcement (with reason).
    """
    return await service.reject_announcement(current_user, announcement_id, data)
