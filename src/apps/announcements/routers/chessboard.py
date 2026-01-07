"""src/apps/announcements/routers/chessboard.py."""

import logging
from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.announcements.schemas.announcement import ResolveRequestSchema
from src.apps.announcements.schemas.chessboard import (
    ChessboardRequestResponse,
    ChessboardRequestCreate,
)
from src.apps.announcements.services.chessboard import ChessboardService
from src.apps.users.models import User
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chessboard Requests"])


@router.post(
    "/{announcement_id}/link-request",
    response_model=ChessboardRequestResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        ResourceAlreadyExistsError,
    ),
)
@inject
async def create_link_request(
    service: FromDishka[ChessboardService],
    announcement_id: int,
    data: ChessboardRequestCreate,
    user: User = Depends(get_current_user),
):
    """
    Submit a request to link an announcement to the chessboard.
    """
    return await service.create_request(user, announcement_id, data)


@router.get("/developer/request", response_model=List[ChessboardRequestResponse])
@inject
async def get_incoming_requests(
    service: FromDishka[ChessboardService],
    user: User = Depends(get_current_user),
):
    """
    (For Developer) Get incoming requests for my housing complexes.
    """
    return await service.get_developer_requests(user)


@router.post(
    "/developer/request/{request_id}/resolve",
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        ResourceAlreadyExistsError,
    ),
)
@inject
async def resolve_request(
    service: FromDishka[ChessboardService],
    request_id: int,
    data: ResolveRequestSchema,
    user: User = Depends(get_current_user),
):
    """
    (For Developer) Approve or reject a request.
    """
    return await service.resolve_request(user, request_id, data.approved, data.comment)
