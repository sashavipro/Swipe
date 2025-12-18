"""src/routes/user_profile.py."""

from fastapi import APIRouter, Depends, UploadFile, File
from dishka.integrations.fastapi import FromDishka, inject

from src.models.users import User
from src.schemas.users import (
    UserResponse,
    EmployeeCreate,
    UserUpdate,
    SubscriptionResponse,
)
from src.routes.deps import get_current_user
from src.services.subscriptions import SubscriptionService
from src.services.user_profile import UserProfileService

router = APIRouter(tags=["User Profile"])


@router.get("/me", response_model=UserResponse)
@inject
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Получить профиль текущего пользователя."""
    return current_user


@router.patch("/me", response_model=UserResponse)
@inject
async def update_profile(
    service: FromDishka[UserProfileService],
    data: UserUpdate,
    user: User = Depends(get_current_user),
):
    """Обновить данные профиля."""
    return await service.update_my_profile(user.id, data)


@router.post("/me/avatar", response_model=UserResponse)
@inject
async def upload_avatar(
    service: FromDishka[UserProfileService],
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Загрузить новую аватарку."""
    return await service.update_avatar(user.id, file)


@router.patch("/me/subscription", response_model=SubscriptionResponse)
@inject
async def toggle_subscription_renewal(
    service: FromDishka[UserProfileService],
    user: User = Depends(get_current_user),
):
    """Переключить автопродление подписки."""
    return await service.toggle_auto_renewal(user.id)


@router.post("/me/subscription/extend", response_model=SubscriptionResponse)
@inject
async def extend_subscription(
    service: FromDishka[SubscriptionService],
    days: int = 30,
    user: User = Depends(get_current_user),
):
    """Продлить подписку."""
    return await service.extend_subscription(user.id, days)


@router.post("/employees", response_model=UserResponse)
@inject
async def create_employee(
    service: FromDishka[UserProfileService],
    data: EmployeeCreate,
):
    """Создание сотрудника."""
    return await service.create_employee(data)
