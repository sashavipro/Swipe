"""src/repositories/houses.py."""

import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.exceptions import ResourceAlreadyExistsError
from src.models.real_estate import (
    House,
    Section,
    Floor,
    Apartment,
    HouseInfo,
    News,
    Document,
)
from src.schemas.real_estate import HouseCreate, NewsCreate, DocumentCreate

logger = logging.getLogger(__name__)


class HouseRepository:
    """
    Репозиторий для работы с домами.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_house_by_id(self, house_id: int) -> House | None:
        """Получить дом по ID со всей информацией."""
        stmt = (
            select(House)
            .options(
                selectinload(House.info),
                selectinload(House.news),
                selectinload(House.documents),
            )
            .where(House.id == house_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_house(self, data: HouseCreate, owner_id: int) -> House:
        """
        Создает полную структуру ЖК.
        """
        logger.info(
            "Attempting to create house structure for: '%s' by owner %s",
            data.name,
            owner_id,
        )

        try:
            house = House(name=data.name, owner_id=owner_id)

            for section_data in data.sections:
                section = Section(name=section_data.name)
                for floor_data in section_data.floors:
                    floor = Floor(number=floor_data.number)
                    for apt_data in floor_data.apartments:
                        apartment = Apartment(number=apt_data.number)
                        floor.apartments.append(apartment)
                    section.floors.append(floor)
                house.sections.append(section)

            if data.info:
                house_info = HouseInfo(**data.info.model_dump())
                house.info = house_info

            self.session.add(house)
            await self.session.flush()

            logger.info(
                "House created successfully: id=%s, name='%s'", house.id, house.name
            )

            return await self.get_house_by_id(house.id)

        except IntegrityError as e:
            logger.warning(
                "Failed to create house: Integrity error (likely duplicate). Error: %s",
                e,
            )
            await self.session.rollback()
            raise ResourceAlreadyExistsError(
                f"House with name '{data.name}' might already exist or constraints violated."
            ) from e

    async def update_house_info(self, house: House, update_data: dict) -> House:
        """Обновляет карточку ЖК."""
        if not house.info:
            house.info = HouseInfo(id=house.id)

        for key, value in update_data.items():
            setattr(house.info, key, value)

        self.session.add(house.info)
        await self.session.flush()

        return await self.get_house_by_id(house.id)

    async def add_news(self, house_id: int, data: NewsCreate) -> News:
        """Добавляет новость к ЖК."""
        news = News(house_id=house_id, **data.model_dump())
        self.session.add(news)
        await self.session.flush()
        return news

    async def delete_news(self, news_id: int):
        """Удаляет новость."""
        stmt = select(News).where(News.id == news_id)
        news = (await self.session.execute(stmt)).scalar_one_or_none()
        if news:
            await self.session.delete(news)
            await self.session.flush()

    async def get_news_by_id(self, news_id: int) -> News | None:
        """Получает новость по ID (для проверки прав)."""
        stmt = select(News).options(selectinload(News.house)).where(News.id == news_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_document(self, house_id: int, data: DocumentCreate) -> Document:
        """Добавляет документ к ЖК."""
        doc = Document(house_id=house_id, **data.model_dump())
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def delete_document(self, doc_id: int):
        """Удаляет документ."""
        stmt = select(Document).where(Document.id == doc_id)
        doc = (await self.session.execute(stmt)).scalar_one_or_none()
        if doc:
            await self.session.delete(doc)
            await self.session.flush()

    async def get_document_by_id(self, doc_id: int) -> Document | None:
        """Получает документ по ID (для проверки прав)."""
        stmt = (
            select(Document)
            .options(selectinload(Document.house))
            .where(Document.id == doc_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_all_houses(self) -> Sequence[House]:
        """Возвращает список домов со всей вложенной структурой и информацией."""
        logger.debug("Fetching all houses with sections/floors/apartments and info")

        query = (
            select(House)
            .options(
                selectinload(House.info),
                selectinload(House.news),
                selectinload(House.documents),
                selectinload(House.sections)
                .selectinload(Section.floors)
                .selectinload(Floor.apartments),
            )
            .order_by(House.id)
        )
        result = await self.session.execute(query)
        items = result.scalars().all()

        logger.debug("Fetched %d houses", len(items))
        return items
