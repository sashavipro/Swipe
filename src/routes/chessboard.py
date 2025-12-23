"""src/routes/chessboard.py."""

import logging
from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.models import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import (
    ChessboardRequestCreate,
    ChessboardRequestResponse,
    ResolveRequestSchema,
)
from src.services.chessboard import ChessboardService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chessboard Requests"])


@router.post(
    "/announcements/{announcement_id}/link-request",
    response_model=ChessboardRequestResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(403, 404, 409),
)
@inject
async def create_link_request(
    service: FromDishka[ChessboardService],
    announcement_id: int,
    data: ChessboardRequestCreate,
    user: User = Depends(get_current_user),
):
    """
    Подать заявку на добавление объявления в шахматку.
    """
    return await service.create_request(user, announcement_id, data)


@router.get("/developer/requests", response_model=List[ChessboardRequestResponse])
@inject
async def get_incoming_requests(
    service: FromDishka[ChessboardService],
    user: User = Depends(get_current_user),
):
    """
    (Для застройщика) Получить входящие заявки на добавление в мои ЖК.
    """
    return await service.get_developer_requests(user)


@router.post(
    "/developer/requests/{request_id}/resolve",
    responses=create_error_responses(403, 404, 409),
)
@inject
async def resolve_request(
    service: FromDishka[ChessboardService],
    request_id: int,
    data: ResolveRequestSchema,
    user: User = Depends(get_current_user),
):
    """
    (Для застройщика) Принять или отклонить заявку.
    """
    return await service.resolve_request(user, request_id, data.approved, data.comment)
