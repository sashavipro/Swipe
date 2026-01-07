"""src/apps/users/repositories/favorite.py."""

import logging
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.apps.announcements.models import Announcement
from src.apps.users.models import Favorite
from src.core.exceptions import ResourceAlreadyExistsError

logger = logging.getLogger(__name__)


class FavoriteRepository:
    """
    Repository for working with favorites.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_favorite(self, user_id: int, announcement_id: int) -> None:
        """Adds an announcement to favorites."""
        logger.info(
            "Adding announcement_id=%s to favorites for user_id=%s",
            announcement_id,
            user_id,
        )

        try:
            favorite = Favorite(user_id=user_id, announcement_id=announcement_id)
            self.session.add(favorite)
            await self.session.flush()

            logger.debug("Successfully added to favorites")

        except IntegrityError as e:
            logger.warning(
                "Failed to add favorite: User %s already has announcement %s",
                user_id,
                announcement_id,
            )
            await self.session.rollback()
            raise ResourceAlreadyExistsError() from e

    async def remove_favorite(self, user_id: int, announcement_id: int) -> None:
        """Removes an announcement from favorites."""
        logger.info(
            "Removing announcement_id=%s from favorites for user_id=%s",
            announcement_id,
            user_id,
        )

        stmt = select(Favorite).where(
            Favorite.user_id == user_id, Favorite.announcement_id == announcement_id
        )
        result = await self.session.execute(stmt)
        chosen = result.scalar_one_or_none()

        if chosen:
            await self.session.delete(chosen)
            await self.session.flush()
            logger.debug("Favorite removed successfully")
        else:
            logger.debug("Favorite not found, nothing to remove (idempotent)")

    async def get_favorite_status(self, user_id: int, announcement_id: int) -> bool:
        """Checks if an announcement is in favorites."""
        stmt = select(Favorite).where(
            Favorite.user_id == user_id, Favorite.announcement_id == announcement_id
        )
        result = await self.session.execute(stmt)
        exists = result.scalar_one_or_none() is not None

        return exists

    async def get_favorites(self, user_id: int) -> list[Announcement]:
        """Returns a list of favorites."""
        logger.debug("Fetching favorites list for user_id=%s", user_id)

        query = (
            select(Announcement)
            .join(Favorite, Favorite.announcement_id == Announcement.id)
            .where(Favorite.user_id == user_id)
            .options(
                selectinload(Announcement.images), selectinload(Announcement.promotion)
            )
            .order_by(Favorite.created_at.desc())
        )
        result = await self.session.execute(query)
        items = result.scalars().all()

        logger.debug("Fetched %d favorite items", len(items))
        return items
