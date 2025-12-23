"""src/repositories/announcements.py."""

import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.exceptions import ResourceAlreadyExistsError
from src.models.real_estate import Announcement, Image, Promotion, DealStatus
from src.schemas.real_estate import AnnouncementCreate

logger = logging.getLogger(__name__)


class AnnouncementRepository:
    """
    Репозиторий для работы с объявлениями.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate, image_urls: list[str]
    ) -> Announcement:
        """
        Создает объявление.
        Если объявление для этой квартиры уже есть и оно ОТКЛОНЕНО или В АРХИВЕ,
        мы его перезаписываем (воскрешаем) и отправляем на модерацию.
        """
        logger.info(
            "Attempting to create announcement for apartment_id=%s by user_id=%s",
            data.apartment_id,
            user_id,
        )

        stmt = (
            select(Announcement)
            .options(selectinload(Announcement.images))
            .where(Announcement.apartment_id == data.apartment_id)
        )
        existing_announcement = (await self.session.execute(stmt)).scalar_one_or_none()

        if existing_announcement:
            if existing_announcement.status in [DealStatus.ACTIVE, DealStatus.PENDING]:
                logger.warning(
                    "Creation failed: Active/Pending announcement exists for apt=%s",
                    data.apartment_id,
                )
                raise ResourceAlreadyExistsError(
                    "Announcement already exists for this apartment and is active or pending."
                )

            logger.info(
                "Overwriting existing (dead) announcement %s", existing_announcement.id
            )

            announcement_data = data.model_dump(exclude={"images"})
            for key, value in announcement_data.items():
                setattr(existing_announcement, key, value)

            existing_announcement.status = DealStatus.PENDING
            existing_announcement.rejection_reason = None
            existing_announcement.user_id = user_id

            existing_announcement.images.clear()
            for url in image_urls:
                image = Image(image_url=url)
                existing_announcement.images.append(image)

            await self.session.flush()
            await self.session.refresh(
                existing_announcement, attribute_names=["images", "promotion"]
            )
            return existing_announcement

        announcement_data = data.model_dump(exclude={"images"})

        announcement = Announcement(
            user_id=user_id, status=DealStatus.PENDING, **announcement_data
        )
        self.session.add(announcement)

        for url in image_urls:
            image = Image(image_url=url)
            announcement.images.append(image)

        await self.session.flush()

        await self.session.refresh(
            announcement, attribute_names=["images", "promotion"]
        )

        logger.info("Announcement created successfully: id=%s", announcement.id)
        return announcement

    async def get_announcements(
        self,
        status: DealStatus | None = DealStatus.ACTIVE,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[Announcement]:
        """
        Получает список объявлений с пагинацией.
        """
        logger.debug("Fetching announcements: limit=%s, offset=%s", limit, offset)

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

        if status:
            query = query.where(Announcement.status == status)

        # Применяем пагинацию
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        items = result.scalars().all()

        logger.debug("Fetched %d announcements", len(items))
        return items

    async def get_announcement_by_criteria(
        self, announcement_id: int | None = None, apartment_id: int | None = None
    ) -> Announcement | None:
        """Ищет объявление по ID или по ID квартиры."""
        logger.debug(
            "Searching announcement: id=%s, apartment_id=%s",
            announcement_id,
            apartment_id,
        )

        stmt = select(Announcement).options(selectinload(Announcement.images))

        if announcement_id:
            stmt = stmt.where(Announcement.id == announcement_id)
        elif apartment_id:
            stmt = stmt.where(Announcement.apartment_id == apartment_id)
        else:
            return None

        result = await self.session.execute(stmt)
        announcement = result.scalar_one_or_none()

        if not announcement:
            logger.debug("Announcement not found for given criteria")

        return announcement

    async def change_status(
        self,
        announcement: Announcement,
        new_status: DealStatus,
        rejection_reason: str | None = None,
    ) -> Announcement:
        """Меняет статус объявления."""
        announcement.status = new_status
        if rejection_reason:
            announcement.rejection_reason = rejection_reason

        self.session.add(announcement)
        await self.session.flush()
        return announcement

    async def update_announcement(
        self, announcement: Announcement, data: dict
    ) -> Announcement:
        """Обновляет поля объявления."""
        logger.info("Updating announcement_id=%s", announcement.id)

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
        logger.info("Deleting announcement_id=%s", announcement.id)

        await self.session.delete(announcement)
        await self.session.flush()
