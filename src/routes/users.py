"""src/routes/users.py."""

from fastapi import APIRouter, Depends, UploadFile, File
from dishka.integrations.fastapi import FromDishka, inject

from src.models.users import User
from src.schemas.users import (
    UserResponse,
    EmployeeCreate,
    UserUpdate,
    SubscriptionResponse,
)
from src.services.users import UserService
from src.routes.deps import get_current_user

router = APIRouter(tags=["Users Management"])


@router.get("/me", response_model=UserResponse)
@inject
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Получить профиль текущего авторизованного пользователя.
    """
    return current_user


@router.post("/employees", response_model=UserResponse)
@inject
async def create_employee(
    service: FromDishka[UserService],
    data: EmployeeCreate,
):
    """
    Создание сотрудника.
    """
    return await service.create_employee(data)


@router.patch("/me", response_model=UserResponse)
@inject
async def update_profile(
    service: FromDishka[UserService],
    data: UserUpdate,
    user: User = Depends(get_current_user),
):
    """
    Обновить данные профиля
    """
    return await service.update_my_profile(user.id, data)


@router.post("/me/avatar", response_model=UserResponse)
@inject
async def upload_avatar(
    service: FromDishka[UserService],
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Загрузить новую аватарку."""
    return await service.update_avatar(user.id, file)


@router.patch("/me/subscription", response_model=SubscriptionResponse)
@inject
async def toggle_subscription_renewal(
    service: FromDishka[UserService],
    user: User = Depends(get_current_user),
):
    """Переключить автопродление подписки."""
    return await service.toggle_auto_renewal(user.id)


@router.post("/me/subscription/extend", response_model=SubscriptionResponse)
@inject
async def extend_subscription(
    service: FromDishka[UserService],
    days: int = 30,
    user: User = Depends(get_current_user),
):
    """
    Продлить подписку на N дней.
    Если подписки нет - создаст новую.
    """
    return await service.extend_subscription(user.id, days)
