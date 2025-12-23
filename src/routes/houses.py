"""src/routes/houses.py."""

import logging
from typing import List
from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from dishka.integrations.fastapi import FromDishka, inject

from src.common.docs import create_error_responses
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
    responses=create_error_responses(409, 422, 403),
)
@inject
async def create_house(
    service: FromDishka[HouseService],
    data: HouseCreate,
    user: User = Depends(get_current_user),
):
    """
    Создать структуру дома (Только для Developer/Moderator).
    """
    logger.info("Creating new house structure: %s", data.name)
    return await service.create_house(user, data)


@router.get("/houses", response_model=List[HouseResponse])
@inject
async def get_houses(
    service: FromDishka[HouseService],
):
    """Получить список всех домов."""
    return await service.get_houses()


@router.patch(
    "/houses/{house_id}/info",
    response_model=HouseResponse,
    responses=create_error_responses(403, 404, 422),
)
@inject
async def update_house_info(
    service: FromDishka[HouseService],
    house_id: int,
    data: HouseInfoUpdate,
    user: User = Depends(get_current_user),
):
    """
    Редактировать текстовую информацию о ЖК (Карточку).
    Только владелец (Застройщик).
    """
    logger.info("User %s updating info for house %s", user.id, house_id)
    return await service.update_house_info(user, house_id, data)


@router.post(
    "/houses/{house_id}/main-image",
    response_model=HouseResponse,
    responses=create_error_responses(403, 404, 422),
)
@inject
async def upload_house_main_image(
    service: FromDishka[HouseService],
    house_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """
    Загрузить главную картинку ЖК.
    Старая картинка будет удалена.
    """
    logger.info("User %s uploading main image for house %s", user.id, house_id)
    return await service.upload_main_image(user, house_id, file)


@router.post(
    "/houses/{house_id}/news",
    response_model=NewsResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(403, 404, 422),
)
@inject
async def add_news(
    service: FromDishka[HouseService],
    house_id: int,
    data: NewsCreate,
    user: User = Depends(get_current_user),
):
    """Добавить новость к ЖК."""
    logger.info("User %s adding news to house %s", user.id, house_id)
    return await service.add_news(user, house_id, data)


@router.delete(
    "/houses/news/{news_id}",
    responses=create_error_responses(403, 404),
)
@inject
async def delete_news(
    service: FromDishka[HouseService],
    news_id: int,
    user: User = Depends(get_current_user),
):
    """Удалить новость."""
    return await service.delete_news(user, news_id)


@router.post(
    "/houses/{house_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses(403, 404, 422),
)
@inject
async def add_document(
    service: FromDishka[HouseService],
    house_id: int,
    file: UploadFile = File(...),
    is_excel: bool = Form(False),
    user: User = Depends(get_current_user),
):
    """Добавить документ к ЖК (загрузка файла)."""
    logger.info("User %s uploading document for house %s", user.id, house_id)
    return await service.add_document(user, house_id, file, is_excel)


@router.delete(
    "/houses/documents/{doc_id}",
    responses=create_error_responses(403, 404),
)
@inject
async def delete_document(
    service: FromDishka[HouseService],
    doc_id: int,
    user: User = Depends(get_current_user),
):
    """Удалить документ."""
    return await service.delete_document(user, doc_id)
