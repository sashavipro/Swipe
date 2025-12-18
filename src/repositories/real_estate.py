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
from src.schemas.real_estate import HouseCreate, AnnouncementCreate, PromotionCreate


class RealEstateRepository:
    """
    Репозиторий для работы с объектами недвижимости.
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

    async def save_image(self, image_url: str) -> Image:
        """Сохраняет ссылку на изображение в БД."""
        image = Image(image_url=image_url)
        self.session.add(image)
        await self.session.flush()
        return image

    async def create_promotion(
        self,
        announcement_id: int,
        data: PromotionCreate,
        user_id: int | None = None,
    ) -> Promotion:
        """
        Создает запись о продвижении.
        Если передан user_id, проверяет, что объявление принадлежит этому пользователю.
        """
        stmt = (
            select(Announcement)
            .options(selectinload(Announcement.promotion))
            .where(Announcement.id == announcement_id)
        )
        announcement = (await self.session.execute(stmt)).scalar_one_or_none()

        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        if user_id is not None and announcement.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to add promotion to this announcement",
            )

        if announcement.promotion:
            raise HTTPException(
                status_code=400, detail="Promotion already exists for this announcement"
            )

        promotion_data = data.model_dump()

        promo = Promotion(announcement_id=announcement_id, **promotion_data)

        self.session.add(promo)
        await self.session.flush()
        return promo

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate, image_urls: list[str]
    ) -> Announcement:
        """
        Создает объявление, привязывает к квартире и добавляет картинки.
        """
        stmt = select(Announcement).where(
            Announcement.apartment_id == data.apartment_id
        )
        if (await self.session.execute(stmt)).scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail="Announcement already exists for this apartment"
            )

        announcement_data = data.model_dump(exclude={"images"})

        announcement = Announcement(user_id=user_id, **announcement_data)
        self.session.add(announcement)

        for url in image_urls:
            image = Image(image_url=url)
            announcement.images.append(image)

        await self.session.flush()

        await self.session.refresh(
            announcement, attribute_names=["images", "promotion"]
        )

        return announcement

    async def get_announcements(self) -> Sequence[Announcement]:
        """
        Получает список всех объявлений.
        """
        query = (
            select(Announcement)
            .options(
                selectinload(Announcement.images), selectinload(Announcement.promotion)
            )
            .outerjoin(Promotion)
            .order_by(
                Promotion.is_turbo.desc().nullslast(), Announcement.created_at.desc()
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_announcement_by_criteria(
        self, announcement_id: int | None = None, apartment_id: int | None = None
    ) -> Announcement | None:
        """
        Ищет объявление по ID или по ID квартиры.
        """
        stmt = select(Announcement).options(selectinload(Announcement.images))

        if announcement_id:
            stmt = stmt.where(Announcement.id == announcement_id)
        elif apartment_id:
            stmt = stmt.where(Announcement.apartment_id == apartment_id)
        else:
            return None

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_announcement(self, announcement: Announcement) -> None:
        """Удаляет объявление из базы."""
        await self.session.delete(announcement)
        await self.session.flush()

    async def get_promotion_by_id(self, promotion_id: int) -> Promotion | None:
        """
        Ищет продвижение по ID.
        """
        stmt = (
            select(Promotion)
            .options(selectinload(Promotion.announcement))
            .where(Promotion.id == promotion_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_promotion(self, promotion: Promotion) -> None:
        """Удаляет запись о продвижении."""
        await self.session.delete(promotion)
        await self.session.flush()

    async def update_announcement(
        self, announcement: Announcement, data: dict
    ) -> Announcement:
        """Обновляет поля объявления."""
        for key, value in data.items():
            if hasattr(announcement, key):
                setattr(announcement, key, value)

        self.session.add(announcement)
        await self.session.flush()
        await self.session.refresh(
            announcement,
            attribute_names=["images", "promotion", "updated_at", "created_at"],
        )
        return announcement

    async def update_promotion(self, promotion: Promotion, data: dict) -> Promotion:
        """Обновляет поля продвижения."""
        for key, value in data.items():
            if hasattr(promotion, key):
                setattr(promotion, key, value)

        self.session.add(promotion)
        await self.session.flush()
        return promotion
