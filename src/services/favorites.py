"""src/services/favorites.py."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from src.repositories.favorites import FavoriteRepository
from src.schemas.real_estate import AnnouncementResponse

logger = logging.getLogger(__name__)


class FavoriteService:
    """
    Service for working with favorites.
    """

    def __init__(self, repo: FavoriteRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def add_to_favorites(self, user_id: int, announcement_id: int):
        """Add to favorites."""
        logger.info(
            "User %s adding announcement %s to favorites", user_id, announcement_id
        )

        try:
            await self.repo.add_favorite(user_id, announcement_id)
            await self.session.commit()

            logger.info(
                "Announcement %s added to favorites for user %s",
                announcement_id,
                user_id,
            )

        except ResourceAlreadyExistsError:
            logger.info(
                "Announcement %s is already in favorites for user %s",
                announcement_id,
                user_id,
            )
            raise

        except Exception as e:
            err_msg = str(e)
            if (
                "ForeignKeyViolation" in err_msg
                or "violates foreign key constraint" in err_msg
            ):
                logger.warning(
                    "Failed to add favorite: Announcement %s not found", announcement_id
                )
                raise ResourceNotFoundError() from e

            logger.error("Unexpected error adding favorite: %s", e, exc_info=True)
            raise

        return {"status": "added", "announcement_id": announcement_id}

    async def remove_from_favorites(self, user_id: int, announcement_id: int):
        """
        Remove from favorites.
        """
        logger.info(
            "User %s removing announcement %s from favorites", user_id, announcement_id
        )

        await self.repo.remove_favorite(user_id, announcement_id)
        await self.session.commit()

        return {"status": "removed", "announcement_id": announcement_id}

    async def get_my_favorites(self, user_id: int) -> list[AnnouncementResponse]:
        """
        Get favorites.
        """
        logger.debug("Fetching favorites for user %s", user_id)
        return await self.repo.get_favorites(user_id)
