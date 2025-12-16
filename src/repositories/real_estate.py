"""src/repositories/real_estate.py."""

from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.real_estate import (
    House,
    Section,
    Floor,
    Announcement,
    Apartment,
    Image,
    Promotion,
)
from src.schemas.real_estate import HouseCreate, AnnouncementCreate


class RealEstateRepository:
    """
    Репозиторий для работы с объектами недвижимости.
    Управляет созданием домов, квартир и объявлений.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_house(self, data: HouseCreate) -> House:
        """
        Создает полную структуру ЖК: Дом -> Секции -> Этажи -> Пустые слоты квартир.
        """
        house = House(name=data.name)

        for section_data in data.sections:
            section = Section(name=section_data.name)

            for floor_data in section_data.floors:
                floor = Floor(number=floor_data.number)

                for _ in floor_data.apartments:
                    apartment = Apartment()
                    floor.apartments.append(apartment)

                section.floors.append(floor)
            house.sections.append(section)

        self.session.add(house)
        await self.session.flush()
        return house

    async def get_all_houses(self) -> Sequence[House]:
        """
        Возвращает список домов со всей вложенной структурой.
        """
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

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate
    ) -> Announcement:
        """
        Создает объявление, привязывает к квартире, добавляет картинки и продвижение.
        """
        stmt = select(Announcement).where(
            Announcement.apartment_id == data.apartment_id
        )
        if (await self.session.execute(stmt)).scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Announcement already exists")

        announcement = Announcement(
            user_id=user_id,
            apartment_id=data.apartment_id,
            apartment_number=data.apartment_number,
            area=data.total_area,
            price=data.price,
            description=data.description,
            address=data.address,
            house_type=data.house_type,
            house_class=data.house_class,
            construction_technology=data.construction_technology,
            territory=data.territory,
            distance_to_sea=data.distance_to_sea,
            utilities=data.utilities,
            ceiling_height=data.ceiling_height,
            gas=data.gas,
            heating=data.heating,
            sewerage=data.sewerage,
            water_supply=data.water_supply,
            registration=data.registration,
            calculation_options=data.calculation_options,
            purpose=data.purpose,
            sum_in_contract=data.sum_in_contract,
            founding_document=data.founding_document,
            number_of_rooms=data.rooms,
            layout=data.layout,
            residential_condition=data.residential_condition,
            kitchen_area=data.kitchen_area,
            has_balcony=data.has_balcony,
            agent_commission=data.agent_commission,
            communication_method=data.communication_method,
            latitude=data.latitude,
            longitude=data.longitude,
        )
        self.session.add(announcement)
        await self.session.flush()

        if data.image_ids:
            img_stmt = select(Image).where(Image.id.in_(data.image_ids))
            images = (await self.session.execute(img_stmt)).scalars().all()
            announcement.images.extend(images)

        if data.promotion:
            promo = Promotion(
                announcement_id=announcement.id,
                is_turbo=data.promotion.is_turbo,
                is_colored=data.promotion.is_colored,
                is_large=data.promotion.is_large,
                is_raised=data.promotion.is_raised,
                add_phrase=data.promotion.add_phrase,
                phrase_text=data.promotion.phrase_text,
                color_type=data.promotion.color_type,
                price_turbo=data.promotion.price_turbo,
                price_color=data.promotion.price_color,
                price_large=data.promotion.price_large,
                price_raised=data.promotion.price_raised,
                price_phrase=data.promotion.price_phrase,
            )
            self.session.add(promo)

        return announcement
