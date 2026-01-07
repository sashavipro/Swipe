"""src/apps/users/routers/chat.py."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Form, UploadFile, File
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.users.models import User
from src.apps.users.schemas.chat import MessageResponse
from src.apps.users.services.chat import ChatService
from src.core.docs import create_error_responses
from src.core.enum import UserRole
from src.core.exceptions import (
    AuthenticationFailedError,
    ResourceNotFoundError,
    PermissionDeniedError,
)
from src.infrastructure.depends import get_current_user

router = APIRouter(tags=["Chat"])


@router.post(
    "/messages",
    response_model=MessageResponse,
    responses=create_error_responses(AuthenticationFailedError, ResourceNotFoundError),
)
@inject
async def send_message(
    service: FromDishka[ChatService],
    recipient_id: int = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message with optional text content and/or a file attachment.
    """
    return await service.send_message(
        sender_id=current_user.id, recipient_id=recipient_id, content=content, file=file
    )


@router.get("/messages/sent", response_model=List[MessageResponse])
@inject
async def get_sent_messages(
    service: FromDishka[ChatService],
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
):
    """
    Get a list of messages sent by you.
    """
    return await service.get_my_sent_messages(current_user.id, limit, offset)


@router.get("/messages/received", response_model=List[MessageResponse])
@inject
async def get_received_messages(
    service: FromDishka[ChatService],
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
):
    """
    Get a list of messages received by you.
    """
    return await service.get_my_received_messages(current_user.id, limit, offset)


@router.get(
    "/messages/chat/{user_a_id}/{user_b_id}",
    response_model=List[MessageResponse],
    responses=create_error_responses(AuthenticationFailedError, PermissionDeniedError),
)
@inject
async def get_chat_history(
    user_a_id: int,
    user_b_id: int,
    service: FromDishka[ChatService],
    current_user: User = Depends(get_current_user),
):
    """
    Get all messages between two specific users.
    ACCESS: MODERATOR ONLY.
    """
    if current_user.role != UserRole.MODERATOR:
        raise PermissionDeniedError("Access restricted to moderators only")

    return await service.get_chat_history(user_a_id, user_b_id)
