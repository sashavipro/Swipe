"""src/apps/users/services/chat.py."""

import logging
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.users.repositories.chat import ChatRepository
from src.apps.users.repositories.user_profile import UserRepository
from src.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from src.infrastructure.storage import ImageStorage

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for handling chat business logic.
    """

    def __init__(
        self,
        repo: ChatRepository,
        user_repo: UserRepository,
        storage: ImageStorage,
        session: AsyncSession,
    ):
        """
        Initializes the service with required repositories.
        """
        self.repo = repo
        self.user_repo = user_repo
        self.storage = storage
        self.session = session

    async def send_message(
        self,
        sender_id: int,
        recipient_id: int,
        content: str = None,
        file: UploadFile = None,  # Добавляем файл
    ):
        """
        Sends a message with an optional file attachment.
        """
        recipient = await self.user_repo.get_by_id(recipient_id)
        if not recipient:
            raise ResourceNotFoundError("Recipient not found")

        if sender_id == recipient_id:
            raise PermissionDeniedError("You cannot send a message to yourself")

        file_url = None
        if file:
            file_url = await self.storage.upload_file(
                file.file,
                folder=f"chats/{sender_id}_{recipient_id}",
                filename=file.filename,
            )

        message = await self.repo.create(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            file_url=file_url,
        )
        await self.session.commit()
        return message

    async def get_my_sent_messages(self, user_id: int, limit: int, offset: int):
        """
        Returns messages sent by the current user.
        """
        return await self.repo.get_sent_messages(user_id, limit, offset)

    async def get_my_received_messages(self, user_id: int, limit: int, offset: int):
        """
        Returns messages received by the current user.
        """
        return await self.repo.get_received_messages(user_id, limit, offset)

    async def get_chat_history(self, user_a_id: int, user_b_id: int):
        """
        Returns the dialogue between any two users (for moderation purposes).
        """
        return await self.repo.get_conversation(user_a_id, user_b_id)
