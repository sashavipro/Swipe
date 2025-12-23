"""src/repositories/houses.py."""

import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.exceptions import ResourceAlreadyExistsError
from src.models.real_estate import House, Section, Floor, Apartment
from src.schemas.real_estate import HouseCreate

logger = logging.getLogger(__name__)


class HouseRepository:
    """
    Репозиторий для работы с домами.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_house(self, data: HouseCreate) -> House:
        """Создает полную структуру ЖК."""
        logger.info("Attempting to create house structure for: '%s'", data.name)

        try:
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

            logger.info(
                "House created successfully: id=%s, name='%s'", house.id, house.name
            )
            return house

        except IntegrityError as e:
            logger.warning(
                "Failed to create house: Integrity error (likely duplicate). Error: %s",
                e,
            )
            await self.session.rollback()
            raise ResourceAlreadyExistsError(
                f"House with name '{data.name}' might already exist or violates constraints."
            ) from e

    async def get_all_houses(self) -> Sequence[House]:
        """Возвращает список домов со всей вложенной структурой."""
        logger.debug("Fetching all houses with sections/floors/apartments")

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
        items = result.scalars().all()

        logger.debug("Fetched %d houses", len(items))
        return items
