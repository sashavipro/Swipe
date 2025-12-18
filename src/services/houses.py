"""src/services/houses.py."""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.houses import HouseRepository
from src.schemas.real_estate import HouseCreate, HouseResponse


class HouseService:
    """
    Сервис для работы с домами.
    """

    def __init__(self, repo: HouseRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_house(self, data: HouseCreate) -> HouseResponse:
        """Создает ЖК со всей структурой."""
        house = await self.repo.create_house(data)
        await self.session.commit()
        return house

    async def get_houses(self) -> Sequence[HouseResponse]:
        """Возвращает список всех ЖК."""
        return await self.repo.get_all_houses()
