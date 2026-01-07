"""src/apps/users/repositories/chat.py."""

from typing import Sequence
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.users.models import Message


class ChatRepository:
    """
    Repository for managing message persistence and retrieval.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.
        """
        self.session = session

    async def create(
        self,
        sender_id: int,
        recipient_id: int,
        content: str = None,
        file_url: str = None,
    ) -> Message:
        """
        Creates and saves a new message to the database.
        """
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            file_url=file_url,
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_sent_messages(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> Sequence[Message]:
        """
        Retrieves a list of messages sent by the specified user.
        """
        stmt = (
            select(Message)
            .where(Message.sender_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_received_messages(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> Sequence[Message]:
        """
        Retrieves a list of messages received by the specified user.
        """
        stmt = (
            select(Message)
            .where(Message.recipient_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_conversation(
        self, user_a: int, user_b: int, limit: int = 50
    ) -> Sequence[Message]:
        """
        Retrieves the chat history between two specific users.
        """
        stmt = (
            select(Message)
            .where(
                or_(
                    and_(Message.sender_id == user_a, Message.recipient_id == user_b),
                    and_(Message.sender_id == user_b, Message.recipient_id == user_a),
                )
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
