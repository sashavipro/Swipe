"""src/apps/users/routers/saved_searches.py."""

import logging
from typing import List
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status, Depends
from src.apps.announcements.schemas.announcement import (
    AnnouncementResponse,
)
from src.apps.announcements.services.announcement import AnnouncementService
from src.apps.users.models import User
from src.apps.users.schemas.saved_searches import SavedSearchResponse, SavedSearchCreate
from src.apps.users.services.saved_searches import SavedSearchService
from src.core.pagination import Pagination
from src.infrastructure.depends import get_current_user
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Saved Searches"])


@router.post(
    "/me/saved-searches",
    response_model=SavedSearchResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(AuthenticationFailedError),
)
@inject
async def create_saved_search(
    service: FromDishka[SavedSearchService],
    data: SavedSearchCreate,
    user: User = Depends(get_current_user),
):
    """
    Save search filter.
    """
    return await service.create_saved_search(user, data)


@router.get(
    "/me/saved-searches",
    response_model=List[SavedSearchResponse],
    responses=create_error_responses(AuthenticationFailedError),
)
@inject
async def get_my_saved_searches(
    service: FromDishka[SavedSearchService],
    user: User = Depends(get_current_user),
):
    """
    Get all saved filters for the current user.
    """
    return await service.get_my_searches(user)


@router.delete(
    "/me/saved-searches/{search_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_saved_search(
    service: FromDishka[SavedSearchService],
    search_id: int,
    user: User = Depends(get_current_user),
):
    """
    Delete saved filter.
    """
    return await service.delete_saved_search(user, search_id)


@router.get(
    "/me/saved-searches/{search_id}/run",
    response_model=List[AnnouncementResponse],
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def run_saved_search(
    search_id: int,
    saved_search_service: FromDishka[SavedSearchService],
    announcement_service: FromDishka[AnnouncementService],
    user: User = Depends(get_current_user),
    pagination: Pagination = Depends(),
):
    """
    Run search using a saved filter.
    """
    saved_search = await saved_search_service.get_saved_search_by_id(user, search_id)

    filter_params = saved_search_service.build_filter_from_saved(saved_search)

    return await announcement_service.search_announcements(
        filter_params, pagination.limit, pagination.offset
    )
