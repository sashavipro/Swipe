"""src/services/real_estate.py."""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.real_estate import RealEstateRepository
from src.schemas.real_estate import (
    HouseCreate,
    HouseResponse,
    AnnouncementCreate,
    AnnouncementResponse,
)


class RealEstateService:
    """
    Сервис для работы с недвижимостью.
    """

    def __init__(self, repo: RealEstateRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_house(self, data: HouseCreate) -> HouseResponse:
        """
        Создает ЖК со всей структурой.
        """
        house = await self.repo.create_house(data)
        await self.session.commit()
        return house

    async def get_houses(self) -> Sequence[HouseResponse]:
        """
        Возвращает список всех ЖК.
        """
        return await self.repo.get_all_houses()

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate
    ) -> AnnouncementResponse:
        """
        Создает объявление о продаже.
        """
        announcement = await self.repo.create_announcement(user_id, data)
        await self.session.commit()
        return announcement
