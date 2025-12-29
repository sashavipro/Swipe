"""src/repositories/announcements.py."""

import logging
from typing import Sequence
from sqlalchemy import select, or_, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.exceptions import ResourceAlreadyExistsError
from src.models.real_estate import Announcement, Image, Promotion, DealStatus
from src.schemas.real_estate import AnnouncementCreate, AnnouncementFilter

logger = logging.getLogger(__name__)


class AnnouncementRepository:
    """
    Repository for working with announcements.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate, image_urls: list[str]
    ) -> Announcement:
        """
        Creates an announcement.
        """
        logger.info("Creating announcement for user_id=%s", user_id)

        if data.apartment_id:
            stmt = (
                select(Announcement)
                .options(selectinload(Announcement.images))
                .where(Announcement.apartment_id == data.apartment_id)
            )
            existing_announcement = (
                await self.session.execute(stmt)
            ).scalar_one_or_none()

            if existing_announcement:
                if existing_announcement.status in [
                    DealStatus.ACTIVE,
                    DealStatus.PENDING,
                ]:
                    logger.warning(
                        "Creation failed: Active/Pending announcement exists for apt=%s",
                        data.apartment_id,
                    )
                    raise ResourceAlreadyExistsError(
                        "Announcement already exists for this apartment and is active or pending."
                    )

                logger.info(
                    "Overwriting existing (dead) announcement %s",
                    existing_announcement.id,
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
        Retrieves a list of announcements with pagination.
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

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        items = result.scalars().all()

        logger.debug("Fetched %d announcements", len(items))
        return items

    async def get_announcement_by_criteria(
        self, announcement_id: int | None = None, apartment_id: int | None = None
    ) -> Announcement | None:
        """Searches for an announcement by ID or by apartment ID."""
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
        """Changes the status of an announcement."""
        announcement.status = new_status
        if rejection_reason:
            announcement.rejection_reason = rejection_reason

        self.session.add(announcement)
        await self.session.flush()
        return announcement

    async def update_announcement(
        self, announcement: Announcement, data: dict
    ) -> Announcement:
        """Updates announcement fields."""
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
        """Deletes an announcement."""
        logger.info("Deleting announcement_id=%s", announcement.id)

        await self.session.delete(announcement)
        await self.session.flush()

    def _apply_market_filters(
        self, query: Select, filter_params: AnnouncementFilter
    ) -> Select:
        """Applies market type filters (Secondary/New)."""
        market_conditions = []
        if filter_params.type_new_buildings:
            market_conditions.append(Announcement.apartment_id.isnot(None))
        if filter_params.type_secondary:
            market_conditions.append(Announcement.apartment_id.is_(None))

        if market_conditions:
            query = query.where(or_(*market_conditions))
        return query

    def _apply_price_area_filters(
        self, query: Select, filter_params: AnnouncementFilter
    ) -> Select:
        """Applies price and area range filters."""
        if filter_params.price_from:
            query = query.where(Announcement.price >= filter_params.price_from)
        if filter_params.price_to:
            query = query.where(Announcement.price <= filter_params.price_to)

        if filter_params.area_from:
            query = query.where(Announcement.area >= filter_params.area_from)
        if filter_params.area_to:
            query = query.where(Announcement.area <= filter_params.area_to)
        return query

    def _apply_other_filters(
        self, query: Select, filter_params: AnnouncementFilter
    ) -> Select:
        """Applies remaining filters."""
        if filter_params.number_of_rooms:
            query = query.where(
                Announcement.number_of_rooms == filter_params.number_of_rooms
            )

        if filter_params.district:
            query = query.where(
                Announcement.address.ilike(f"%{filter_params.district}%")
            )
        if filter_params.microdistrict:
            query = query.where(
                Announcement.address.ilike(f"%{filter_params.microdistrict}%")
            )

        if filter_params.purpose:
            query = query.where(Announcement.purpose == filter_params.purpose)
        if filter_params.condition:
            query = query.where(
                Announcement.residential_condition == filter_params.condition
            )
        if filter_params.house_type:
            query = query.where(Announcement.house_type == filter_params.house_type)
        if filter_params.house_class:
            query = query.where(Announcement.house_class == filter_params.house_class)
        if filter_params.has_balcony is not None:
            query = query.where(Announcement.has_balcony == filter_params.has_balcony)
        return query

    async def search_announcements(
        self,
        filter_params: AnnouncementFilter,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[Announcement]:
        """
        Searching announcements by filter.
        """
        logger.debug("Searching announcements with filter: %s", filter_params)

        query = (
            select(Announcement)
            .where(Announcement.status == DealStatus.ACTIVE)
            .options(
                selectinload(Announcement.images), selectinload(Announcement.promotion)
            )
            .outerjoin(Promotion)
            .order_by(
                Promotion.is_turbo.desc().nullslast(), Announcement.created_at.desc()
            )
        )

        if filter_params.status_house:
            query = query.where(Announcement.status == filter_params.status_house)
        else:
            query = query.where(Announcement.status == DealStatus.ACTIVE)

        query = self._apply_market_filters(query, filter_params)
        query = self._apply_price_area_filters(query, filter_params)
        query = self._apply_other_filters(query, filter_params)

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        items = result.scalars().all()

        logger.debug("Found %d announcements", len(items))
        return items
