"""src/apps/admin/routers/crud_user.py."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.admin.schemas import (
    DeveloperCreate,
    NotaryCreate,
    AgentCreate,
    ModeratorCreate,
    SimpleUserCreate,
    UserUpdateByAdmin,
)
from src.apps.admin.services.crud_user import CrudUserService
from src.apps.users.models import User
from src.apps.users.schemas.user_profile import UserResponse
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.enum import UserRole
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin Users"])


@router.get(
    "/users",
    response_model=List[UserResponse],
    responses=create_error_responses(AuthenticationFailedError, PermissionDeniedError),
)
@inject
async def get_all_users(
    service: FromDishka[CrudUserService],
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    user: User = Depends(get_current_user),
):
    """
    Get all users list.
    """
    return await service.get_users(user, role)


@router.post(
    "/users/developers",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceAlreadyExistsError
    ),
)
@inject
async def create_developer(
    service: FromDishka[CrudUserService],
    data: DeveloperCreate,
    user: User = Depends(get_current_user),
):
    """Create Developer."""
    logger.info("Admin %s creating developer %s", user.id, data.email)
    return await service.create_developer(user, data)


@router.post(
    "/users/notaries",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceAlreadyExistsError
    ),
)
@inject
async def create_notary(
    service: FromDishka[CrudUserService],
    data: NotaryCreate,
    user: User = Depends(get_current_user),
):
    """Create Notary."""
    logger.info("Admin %s creating notary %s", user.id, data.email)
    return await service.create_notary(user, data)


@router.post(
    "/users/agents",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceAlreadyExistsError
    ),
)
@inject
async def create_agent(
    service: FromDishka[CrudUserService],
    data: AgentCreate,
    user: User = Depends(get_current_user),
):
    """Create Agent."""
    logger.info("Admin %s creating agent %s", user.id, data.email)
    return await service.create_agent(user, data)


@router.post(
    "/users/moderators",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceAlreadyExistsError
    ),
)
@inject
async def create_moderator(
    service: FromDishka[CrudUserService],
    data: ModeratorCreate,
    user: User = Depends(get_current_user),
):
    """Create new Moderator."""
    logger.info("Admin %s creating moderator %s", user.id, data.email)
    return await service.create_moderator(user, data)


@router.post(
    "/users/simple",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceAlreadyExistsError
    ),
)
@inject
async def create_simple_user(
    service: FromDishka[CrudUserService],
    data: SimpleUserCreate,
    user: User = Depends(get_current_user),
):
    """Create simple user manually."""
    logger.info("Admin %s creating simple user %s", user.id, data.email)
    return await service.create_simple_user(user, data)


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        ResourceAlreadyExistsError,
    ),
)
@inject
async def update_user(
    service: FromDishka[CrudUserService],
    user_id: int,
    data: UserUpdateByAdmin,
    user: User = Depends(get_current_user),
):
    """Edit user (including role change)."""
    return await service.update_user_by_moderator(user, user_id, data)


@router.delete(
    "/users/{user_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_user(
    service: FromDishka[CrudUserService],
    user_id: int,
    user: User = Depends(get_current_user),
):
    """Delete user."""
    return await service.delete_user_by_moderator(user, user_id)
