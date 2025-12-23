"""src/routes/admin/complaints.py."""

from typing import List
from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.models import User
from src.routes.deps import get_current_user
from src.schemas.users import ComplaintCreate, ComplaintResponse
from src.services.admin import AdminService

router = APIRouter(tags=["Complaints"])


@router.post(
    "/complaints",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(401, 403, 404, 422),
)
@inject
async def report_user(
    data: ComplaintCreate,
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """Пожаловаться на пользователя (Любой авторизованный юзер)."""
    return await service.report_user(current_user, data)


@router.get(
    "/complaints",
    response_model=List[ComplaintResponse],
    responses=create_error_responses(401, 403),
)
@inject
async def list_complaints(
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """Просмотр активных жалоб (Только Модератор)."""
    return await service.get_complaints(current_user)


@router.post(
    "/complaints/{complaint_id}/resolve",
    responses=create_error_responses(401, 403, 404),
)
@inject
async def resolve_complaint(
    complaint_id: int,
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """Закрыть (решить) жалобу (Только Модератор)."""
    return await service.resolve_complaint(current_user, complaint_id)
