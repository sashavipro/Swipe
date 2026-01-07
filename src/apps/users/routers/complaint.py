"""src/apps/users/routers/complaint.py."""

from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.users.models import User
from src.apps.users.schemas.complaint import ComplaintResponse, ComplaintCreate
from src.apps.users.services.complaint import ComplaintService
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceNotFoundError,
)

router = APIRouter(tags=["Complaints"])


@router.post(
    "/complaints",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def report_user(
    data: ComplaintCreate,
    service: FromDishka[ComplaintService],
    current_user: User = Depends(get_current_user),
):
    """
    Report a user.
    (Any authenticated user).
    """
    return await service.report_user(current_user, data)


@router.get(
    "/complaints",
    response_model=List[ComplaintResponse],
    responses=create_error_responses(AuthenticationFailedError, PermissionDeniedError),
)
@inject
async def list_complaints(
    service: FromDishka[ComplaintService],
    current_user: User = Depends(get_current_user),
):
    """
    View active complaints.
    (Moderator only).
    """
    return await service.get_complaints(current_user)


@router.post(
    "/complaints/{complaint_id}/resolve",
    responses=create_error_responses(AuthenticationFailedError, PermissionDeniedError),
)
@inject
async def resolve_complaint(
    complaint_id: int,
    service: FromDishka[ComplaintService],
    current_user: User = Depends(get_current_user),
):
    """
    Resolve (close) a complaint.
    (Moderator only).
    """
    return await service.resolve_complaint(current_user, complaint_id)
