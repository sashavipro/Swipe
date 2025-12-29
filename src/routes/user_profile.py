"""src/routes/user_profile.py."""

import logging

from fastapi import APIRouter, Depends, UploadFile, File, status
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.common.exceptions import (
    ResourceAlreadyExistsError,
    AuthenticationFailedError,
    ResourceNotFoundError,
    BadRequestError,
)
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

logger = logging.getLogger(__name__)
router = APIRouter(tags=["User Profile"])


@router.get(
    "/me",
    response_model=UserResponse,
    responses=create_error_responses(AuthenticationFailedError),
)
@inject
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    responses=create_error_responses(
        AuthenticationFailedError, ResourceAlreadyExistsError, ResourceNotFoundError
    ),
)
@inject
async def update_profile(
    service: FromDishka[UserProfileService],
    data: UserUpdate,
    user: User = Depends(get_current_user),
):
    """
    Update profile data.
    """
    logger.info("User %s updating profile", user.id)
    return await service.update_my_profile(user.id, data)


@router.post(
    "/me/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, ResourceNotFoundError, BadRequestError
    ),
)
@inject
async def upload_avatar(
    service: FromDishka[UserProfileService],
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Upload new avatar."""
    logger.info("User %s uploading avatar", user.id)
    return await service.update_avatar(user.id, file)


@router.patch(
    "/me/subscription",
    response_model=SubscriptionResponse,
    responses=create_error_responses(AuthenticationFailedError, ResourceNotFoundError),
)
@inject
async def toggle_subscription_renewal(
    service: FromDishka[SubscriptionService],
    user: User = Depends(get_current_user),
):
    """Toggle auto-renewal of subscription."""
    logger.info("User %s toggling subscription renewal", user.id)
    return await service.toggle_auto_renewal(user.id)


@router.post(
    "/me/subscription/extend",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(AuthenticationFailedError, ResourceNotFoundError),
)
@inject
async def extend_subscription(
    service: FromDishka[SubscriptionService],
    days: int = 30,
    user: User = Depends(get_current_user),
):
    """Extend subscription."""
    logger.info("User %s extending subscription for %d days", user.id, days)
    return await service.extend_subscription(user.id, days)


@router.post(
    "/employees",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(ResourceAlreadyExistsError),
)
@inject
async def create_employee(
    service: FromDishka[UserProfileService],
    data: EmployeeCreate,
):
    """
    Create an employee (agent).
    """
    logger.info("Creating new employee: %s", data.email)
    return await service.create_employee(data)
