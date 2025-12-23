"""src/routes/admin/users.py."""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.models import User
from src.models.users import UserRole
from src.routes.deps import get_current_user
from src.schemas.users import (
    UserResponse,
    EmployeeCreate,
    UserUpdateByAdmin,
)
from src.services.admin import AdminService

router = APIRouter(tags=["Moderator users CRUD"])


@router.get(
    "/users",
    response_model=List[UserResponse],
    responses=create_error_responses(401, 403),
)
@inject
async def get_users_list(
    service: FromDishka[AdminService],
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    current_user: User = Depends(get_current_user),
):
    """Список пользователей."""
    return await service.get_users(current_user, role)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(401, 403, 409, 422),
)
@inject
async def create_user(
    data: EmployeeCreate,
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """Создать пользователя (Только Модератор)."""
    return await service.create_user_by_moderator(current_user, data)


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    responses=create_error_responses(401, 403, 404, 409, 422),
)
@inject
async def update_user(
    user_id: int,
    data: UserUpdateByAdmin,
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """Редактировать пользователя (Только Модератор)."""
    return await service.update_user_by_moderator(current_user, user_id, data)


@router.delete("/users/{user_id}", responses=create_error_responses(401, 403, 404))
@inject
async def delete_user(
    user_id: int,
    service: FromDishka[AdminService],
    current_user: User = Depends(get_current_user),
):
    """Удалить пользователя (Только Модератор)."""
    return await service.delete_user_by_moderator(current_user, user_id)
