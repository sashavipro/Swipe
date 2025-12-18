"""src/repositories/announcements.py."""

from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.real_estate import Announcement, Image, Promotion
from src.schemas.real_estate import AnnouncementCreate


class AnnouncementRepository:
    """
    Репозиторий для работы с объявлениями.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate, image_urls: list[str]
    ) -> Announcement:
        """Создает объявление с картинками."""
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
        """Получает список всех объявлений."""
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
        """Ищет объявление по ID или по ID квартиры."""
        stmt = select(Announcement).options(selectinload(Announcement.images))

        if announcement_id:
            stmt = stmt.where(Announcement.id == announcement_id)
        elif apartment_id:
            stmt = stmt.where(Announcement.apartment_id == apartment_id)
        else:
            return None

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

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

    async def delete_announcement(self, announcement: Announcement) -> None:
        """Удаляет объявление."""
        await self.session.delete(announcement)
        await self.session.flush()
