"""src/apps/announcements/services/chessboard.py."""

import logging
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.announcements.repositories.announcement import AnnouncementRepository
from src.apps.announcements.repositories.chessboard import ChessboardRepository
from src.apps.announcements.schemas.chessboard import (
    ChessboardRequestCreate,
    ChessboardRequestResponse,
)
from src.apps.users.models import User
from src.core.enum import RequestStatus
from src.core.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
)

logger = logging.getLogger(__name__)


class ChessboardService:
    """
    Service for managing chessboard linking requests.
    Allows users to create requests, and developers to moderate them.
    """

    def __init__(
        self,
        repo: ChessboardRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.announcement_repo = announcement_repo
        self.session = session

    async def create_request(
        self, user: User, announcement_id: int, data: ChessboardRequestCreate
    ) -> ChessboardRequestResponse:
        """User submits a link request."""
        announcement = await self.announcement_repo.get_announcement_by_criteria(
            announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError()

        if announcement.user_id != user.id:
            raise PermissionDeniedError()

        if announcement.apartment_id is not None:
            raise ResourceAlreadyExistsError()

        request = await self.repo.create_request(announcement_id, data)
        await self.session.commit()
        return request

    async def get_developer_requests(
        self, developer: User
    ) -> Sequence[ChessboardRequestResponse]:
        """Developer views incoming requests."""
        return await self.repo.get_requests_for_developer(developer.id)

    async def resolve_request(
        self,
        developer: User,
        request_id: int,
        approved: bool,
        comment: str | None = None,
    ):
        """
        Developer makes a decision.
        """
        request = await self.repo.get_request_by_id(request_id)
        if not request:
            raise ResourceNotFoundError()

        if request.house.owner_id != developer.id:
            raise PermissionDeniedError()

        if request.status != RequestStatus.PENDING:
            raise ResourceAlreadyExistsError()

        if not approved:
            await self.repo.update_status(request, RequestStatus.REJECTED, comment)
            await self.session.commit()
            return {"status": "rejected"}

        apartment = await self.repo.find_apartment(
            request.target_house_id,
            request.target_section_id,
            request.target_floor_id,
            request.target_apartment_number,
        )

        if not apartment:
            apartment = await self.repo.create_apartment(
                request.target_floor_id, request.target_apartment_number
            )

        existing_announcement = (
            await self.announcement_repo.get_announcement_by_criteria(
                apartment_id=apartment.id
            )
        )
        if existing_announcement:
            raise ResourceAlreadyExistsError()

        await self.announcement_repo.update_announcement(
            request.announcement, {"apartment_id": apartment.id}
        )

        await self.repo.update_status(request, RequestStatus.APPROVED, comment)

        await self.session.commit()
        return {"status": "approved", "apartment_id": apartment.id}
