"""src/repositories/houses.py."""

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.real_estate import House, Section, Floor, Apartment
from src.schemas.real_estate import HouseCreate


class HouseRepository:
    """
    Репозиторий для работы с домами.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_house(self, data: HouseCreate) -> House:
        """Создает полную структуру ЖК."""
        house = House(name=data.name)
        for section_data in data.sections:
            section = Section(name=section_data.name)
            for floor_data in section_data.floors:
                floor = Floor(number=floor_data.number)
                for apt_data in floor_data.apartments:
                    apartment = Apartment(number=apt_data.number)
                    floor.apartments.append(apartment)
                section.floors.append(floor)
            house.sections.append(section)

        self.session.add(house)
        await self.session.flush()
        return house

    async def get_all_houses(self) -> Sequence[House]:
        """Возвращает список домов."""
        query = (
            select(House)
            .options(
                selectinload(House.sections)
                .selectinload(Section.floors)
                .selectinload(Floor.apartments)
            )
            .order_by(House.id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
