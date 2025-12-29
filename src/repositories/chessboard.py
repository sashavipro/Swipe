"""src/repositories/chessboard.py."""

import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.real_estate import (
    ChessboardRequest,
    RequestStatus,
    House,
    Announcement,
    Apartment,
)
from src.schemas.real_estate import ChessboardRequestCreate

logger = logging.getLogger(__name__)


class ChessboardRepository:
    """
    Repository for working with chessboard linking requests.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(
        self, announcement_id: int, data: ChessboardRequestCreate
    ) -> ChessboardRequest:
        """Creates a new request."""
        request = ChessboardRequest(
            announcement_id=announcement_id,
            target_house_id=data.target_house_id,
            target_section_id=data.target_section_id,
            target_floor_id=data.target_floor_id,
            target_apartment_number=data.target_apartment_number,
            status=RequestStatus.PENDING,
        )
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_request_by_id(self, request_id: int) -> ChessboardRequest | None:
        """Retrieves a request by ID."""
        stmt = (
            select(ChessboardRequest)
            .options(
                selectinload(ChessboardRequest.announcement),
                selectinload(ChessboardRequest.house),
            )
            .where(ChessboardRequest.id == request_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_requests_for_developer(
        self, developer_id: int
    ) -> Sequence[ChessboardRequest]:
        """
        Returns all requests for houses owned by this developer.
        """
        stmt = (
            select(ChessboardRequest)
            .join(House, ChessboardRequest.target_house_id == House.id)
            .options(selectinload(ChessboardRequest.announcement))
            .where(House.owner_id == developer_id)
            .order_by(ChessboardRequest.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_my_requests(self, user_id: int) -> Sequence[ChessboardRequest]:
        """Returns requests created by the user (via their announcements)."""
        stmt = (
            select(ChessboardRequest)
            .join(Announcement, ChessboardRequest.announcement_id == Announcement.id)
            .where(Announcement.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self,
        request: ChessboardRequest,
        status: RequestStatus,
        comment: str | None = None,
    ):
        """Updates the status of a request."""
        request.status = status
        if comment:
            request.developer_comment = comment
        self.session.add(request)
        await self.session.flush()

    async def find_apartment(
        self, _house_id: int, _section_id: int, floor_id: int, number: int
    ) -> Apartment | None:
        """Searches for an existing apartment (cell) in the database."""
        stmt = (
            select(Apartment)
            .join(Apartment.floor)
            .join(
                Apartment.floor.and_(
                    Apartment.floor_id == floor_id,
                )
            )
            .where(Apartment.number == number, Apartment.floor_id == floor_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_apartment(self, floor_id: int, number: int) -> Apartment:
        """Creates a new apartment (cell) in the chessboard."""
        apt = Apartment(floor_id=floor_id, number=number)
        self.session.add(apt)
        await self.session.flush()
        return apt
