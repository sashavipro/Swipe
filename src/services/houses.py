"""src/services/houses.py."""

import logging
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.houses import HouseRepository
from src.schemas.real_estate import HouseCreate, HouseResponse

logger = logging.getLogger(__name__)


class HouseService:
    """
    Сервис для работы с домами.
    """

    def __init__(self, repo: HouseRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_house(self, data: HouseCreate) -> HouseResponse:
        """Создает ЖК со всей структурой."""
        logger.info("Creating new house structure: %s", data.name)

        house = await self.repo.create_house(data)
        await self.session.commit()

        logger.info("House created successfully with id=%s", house.id)
        return house

    async def get_houses(self) -> Sequence[HouseResponse]:
        """Возвращает список всех ЖК."""
        logger.debug("Fetching all houses")
        return await self.repo.get_all_houses()
