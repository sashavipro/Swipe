"""src/apps/buildings/routers.py."""

import logging
from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from dishka.integrations.fastapi import FromDishka, inject

from src.infrastructure.depends import get_current_user
from src.apps.users.models import User
from src.apps.buildings.schemas import (
    HouseCreate,
    HouseResponse,
    HouseInfoUpdate,
    NewsResponse,
    NewsCreate,
    DocumentResponse,
)
from src.apps.buildings.services import HouseService
from src.core.docs import create_error_responses
from src.core.exceptions import (
    AuthenticationFailedError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    BadRequestError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/houses", tags=["Buildings"])


@router.post(
    "/",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceAlreadyExistsError
    ),
)
@inject
async def create_house(
    data: HouseCreate,
    service: FromDishka[HouseService],
    user: User = Depends(get_current_user),
):
    """
    Create a house structure (Only for Developer/Moderator).
    """
    logger.info("Creating new house structure: %s", data.name)
    return await service.create_house(user, data)


@router.get("/", response_model=List[HouseResponse])
@inject
async def get_all_houses(service: FromDishka[HouseService]):
    """Get a list of all houses."""
    return await service.get_houses()


@router.patch(
    "/{house_id}/info",
    response_model=HouseResponse,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def update_info(
    house_id: int,
    data: HouseInfoUpdate,
    service: FromDishka[HouseService],
    user: User = Depends(get_current_user),
):
    """
    Edit house information (Card).
    Only owner (Developer).
    """
    logger.info("User %s updating info for house %s", user.id, house_id)
    return await service.update_house_info(user, house_id, data)


@router.post(
    "/{house_id}/image",
    response_model=HouseResponse,
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        BadRequestError,
    ),
)
@inject
async def upload_house_image(
    service: FromDishka[HouseService],
    house_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """
    Upload the main image of the house.
    Old image will be deleted.
    """
    logger.info("User %s uploading main image for house %s", user.id, house_id)
    return await service.upload_main_image(user, house_id, file)


@router.post(
    "/{house_id}/news",
    response_model=NewsResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def add_house_news(
    house_id: int,
    data: NewsCreate,
    service: FromDishka[HouseService],
    user: User = Depends(get_current_user),
):
    """Add news to the house."""
    logger.info("User %s adding news to house %s", user.id, house_id)
    return await service.add_news(user, house_id, data)


@router.delete(
    "/news/{news_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_house_news(
    news_id: int,
    service: FromDishka[HouseService],
    user: User = Depends(get_current_user),
):
    """Delete news."""
    return await service.delete_news(user, news_id)


@router.post(
    "/{house_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        BadRequestError,
    ),
)
@inject
async def add_house_doc(
    service: FromDishka[HouseService],
    house_id: int,
    file: UploadFile = File(...),
    is_excel: bool = Form(False),
    user: User = Depends(get_current_user),
):
    """Add a document to the house (file upload)."""
    logger.info("User %s uploading document for house %s", user.id, house_id)
    return await service.add_document(user, house_id, file, is_excel)


@router.delete(
    "/documents/{doc_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_house_doc(
    doc_id: int,
    service: FromDishka[HouseService],
    user: User = Depends(get_current_user),
):
    """Delete a document."""
    return await service.delete_document(user, doc_id)
