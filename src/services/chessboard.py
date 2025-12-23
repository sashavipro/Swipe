"""src/services/chessboard.py."""

import logging
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
)
from src.models import User
from src.models.real_estate import RequestStatus
from src.repositories.chessboard import ChessboardRepository
from src.repositories.announcements import AnnouncementRepository
from src.schemas.real_estate import ChessboardRequestCreate, ChessboardRequestResponse

logger = logging.getLogger(__name__)


class ChessboardService:
    """
    Сервис для управления заявками на добавление в шахматку.
    Позволяет пользователям создавать заявки, а застройщикам — модерировать их.
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
        """Пользователь подает заявку на привязку."""
        announcement = await self.announcement_repo.get_announcement_by_criteria(
            announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError("Announcement not found")

        if announcement.user_id != user.id:
            raise PermissionDeniedError("You do not own this announcement")

        if announcement.apartment_id is not None:
            raise ResourceAlreadyExistsError(
                "This announcement is already linked to a chessboard apartment"
            )

        request = await self.repo.create_request(announcement_id, data)
        await self.session.commit()
        return request

    async def get_developer_requests(
        self, developer: User
    ) -> Sequence[ChessboardRequestResponse]:
        """Застройщик смотрит входящие заявки."""
        return await self.repo.get_requests_for_developer(developer.id)

    async def resolve_request(
        self,
        developer: User,
        request_id: int,
        approved: bool,
        comment: str | None = None,
    ):
        """
        Застройщик принимает решение.
        """
        request = await self.repo.get_request_by_id(request_id)
        if not request:
            raise ResourceNotFoundError("Request not found")

        if request.house.owner_id != developer.id:
            raise PermissionDeniedError("You are not the owner of this housing complex")

        if request.status != RequestStatus.PENDING:
            raise ResourceAlreadyExistsError("Request is already resolved")

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
            raise ResourceAlreadyExistsError(
                "This apartment slot is already occupied by another announcement"
            )

        await self.announcement_repo.update_announcement(
            request.announcement, {"apartment_id": apartment.id}
        )

        await self.repo.update_status(request, RequestStatus.APPROVED, comment)

        await self.session.commit()
        return {"status": "approved", "apartment_id": apartment.id}
