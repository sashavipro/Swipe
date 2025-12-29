"""src/routes/houses.py."""

import logging
from typing import List
from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
from src.common.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    AuthenticationFailedError,
    BadRequestError,
)
from src.models.users import User
from src.routes.deps import get_current_user
from src.schemas.real_estate import (
    HouseCreate,
    HouseResponse,
    HouseInfoUpdate,
    NewsCreate,
    NewsResponse,
    DocumentResponse,
)
from src.services.houses import HouseService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["House"])


@router.post(
    "/houses",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceAlreadyExistsError
    ),
)
@inject
async def create_house(
    service: FromDishka[HouseService],
    data: HouseCreate,
    user: User = Depends(get_current_user),
):
    """
    Create a house structure (Only for Developer/Moderator).
    """
    logger.info("Creating new house structure: %s", data.name)
    return await service.create_house(user, data)


@router.get("/houses", response_model=List[HouseResponse])
@inject
async def get_houses(
    service: FromDishka[HouseService],
):
    """Get a list of all houses."""
    return await service.get_houses()


@router.patch(
    "/houses/{house_id}/info",
    response_model=HouseResponse,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def update_house_info(
    service: FromDishka[HouseService],
    house_id: int,
    data: HouseInfoUpdate,
    user: User = Depends(get_current_user),
):
    """
    Edit house information (Card).
    Only owner (Developer).
    """
    logger.info("User %s updating info for house %s", user.id, house_id)
    return await service.update_house_info(user, house_id, data)


@router.post(
    "/houses/{house_id}/main-image",
    response_model=HouseResponse,
    responses=create_error_responses(
        AuthenticationFailedError,
        PermissionDeniedError,
        ResourceNotFoundError,
        BadRequestError,
    ),
)
@inject
async def upload_house_main_image(
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
    "/houses/{house_id}/news",
    response_model=NewsResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def add_news(
    service: FromDishka[HouseService],
    house_id: int,
    data: NewsCreate,
    user: User = Depends(get_current_user),
):
    """Add news to the house."""
    logger.info("User %s adding news to house %s", user.id, house_id)
    return await service.add_news(user, house_id, data)


@router.delete(
    "/houses/news/{news_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_news(
    service: FromDishka[HouseService],
    news_id: int,
    user: User = Depends(get_current_user),
):
    """Delete news."""
    return await service.delete_news(user, news_id)


@router.post(
    "/houses/{house_id}/documents",
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
async def add_document(
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
    "/houses/documents/{doc_id}",
    responses=create_error_responses(
        AuthenticationFailedError, PermissionDeniedError, ResourceNotFoundError
    ),
)
@inject
async def delete_document(
    service: FromDishka[HouseService],
    doc_id: int,
    user: User = Depends(get_current_user),
):
    """Delete a document."""
    return await service.delete_document(user, doc_id)
