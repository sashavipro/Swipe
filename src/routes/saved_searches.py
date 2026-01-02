"""src/routes/saved_searches.py."""

import logging
from typing import List, Annotated, Any
from fastapi import APIRouter, Depends, status, Query
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.common.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    AuthenticationFailedError,
)
from src.models.real_estate import DealStatus, RoomCount
from src.models.users import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import AnnouncementResponse, AnnouncementFilter
from src.schemas.saved_searches import SavedSearchCreate, SavedSearchResponse
from src.services.saved_searches import SavedSearchService
from src.services.announcements import AnnouncementService

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
    limit: Annotated[int, Query(ge=1, le=100, description="Number of records")] = 20,
    offset: Annotated[int, Query(ge=0, description="Offset")] = 0,
):
    """
    Run search using a saved filter.
    """
    saved_search = await saved_search_service.get_saved_search_by_id(user, search_id)

    search_data: dict[str, Any] = {}

    for k, v in saved_search.__dict__.items():
        if k.startswith("_"):
            continue

        if k == "status_house":
            continue

        if k == "number_of_rooms" and v is not None:
            val_str = str(v)
            valid_values = {item.value for item in RoomCount}
            if val_str in valid_values:
                search_data[k] = val_str
            continue

        if k in AnnouncementFilter.model_fields.keys():
            search_data[k] = v

    filter_params = AnnouncementFilter(**search_data)

    if not filter_params.status_house:
        filter_params.status_house = DealStatus.ACTIVE

    return await announcement_service.search_announcements(filter_params, limit, offset)
