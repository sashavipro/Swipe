"""src/services/houses.py."""

import logging
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.houses import HouseRepository
from src.schemas.real_estate import HouseCreate, HouseResponse
from src.models.users import User, UserRole
from src.common.exceptions import PermissionDeniedError

logger = logging.getLogger(__name__)


class HouseService:
    """
    Сервис для работы с домами.
    """

    def __init__(self, repo: HouseRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_house(self, user: User, data: HouseCreate) -> HouseResponse:
        """
        Создает ЖК со всей структурой.
        Доступно только DEVELOPER или MODERATOR.
        """
        if user.role not in [UserRole.DEVELOPER, UserRole.MODERATOR]:
            logger.warning(
                "User %s denied creating house (role: %s)", user.id, user.role
            )
            raise PermissionDeniedError("Only developers can create housing complexes")

        logger.info("Creating new house structure: %s by user %s", data.name, user.id)

        house = await self.repo.create_house(data, owner_id=user.id)
        await self.session.commit()

        logger.info("House created successfully with id=%s", house.id)
        return house

    async def get_houses(self) -> Sequence[HouseResponse]:
        """Возвращает список всех ЖК."""
        logger.debug("Fetching all houses")
        return await self.repo.get_all_houses()
