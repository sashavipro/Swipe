"""src/apps/announcements/routers/announcement.py."""

import logging
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, Query
from dishka.integrations.fastapi import FromDishka, inject

from src.apps.announcements.schemas.announcement import (
    AnnouncementResponse,
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementFilter,
)
from src.apps.announcements.services.announcement import AnnouncementService
from src.apps.users.models import User
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    ResourceAlreadyExistsError,
    BadRequestError,
    PermissionDeniedError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.post(
    "/",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, ResourceAlreadyExistsError, BadRequestError
    ),
)
@inject
async def create_announcement(
    service: FromDishka[AnnouncementService],
    data: AnnouncementCreate,
    user: User = Depends(get_current_user),
):
    """
    Create a new announcement.
    """
    logger.info("User %s creating announcement", user.id)
    return await service.create_announcement(user.id, data)


@router.get("/", response_model=List[AnnouncementResponse])
@inject
async def get_announcements(
    service: FromDishka[AnnouncementService],
    limit: Annotated[
        int, Query(ge=1, le=100, description="Number of records (max 100)")
    ] = 20,
    offset: Annotated[int, Query(ge=0, description="Offset")] = 0,
):
    """
    Get a list of announcements with pagination.
    """
    return await service.get_announcements(limit=limit, offset=offset)


@router.patch(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        BadRequestError,
    ),
)
@inject
async def update_announcement(
    service: FromDishka[AnnouncementService],
    announcement_id: int,
    data: AnnouncementUpdate,
    user: User = Depends(get_current_user),
):
    """
    Update an announcement.
    """
    logger.info("User %s updating announcement %s", user.id, announcement_id)
    return await service.update_announcement(user, announcement_id, data)


@router.delete(
    "/{announcement_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_announcement_by_id(
    service: FromDishka[AnnouncementService],
    announcement_id: int,
    user: User = Depends(get_current_user),
):
    """
    Delete an announcement.
    """
    logger.info("User %s deleting announcement %s", user.id, announcement_id)
    return await service.delete_announcement(user, announcement_id=announcement_id)


@router.get(
    "/search",
    response_model=List[AnnouncementResponse],
    responses=create_error_responses(BadRequestError),
)
@inject
async def search_announcements(
    service: FromDishka[AnnouncementService],
    filter_params: AnnouncementFilter = Depends(),
    limit: Annotated[
        int, Query(ge=1, le=100, description="Number of records (max 100)")
    ] = 20,
    offset: Annotated[int, Query(ge=0, description="Offset")] = 0,
):
    """
    Search announcements by filter.
    Parameters are passed in the query string.
    """
    return await service.search_announcements(filter_params, limit, offset)
