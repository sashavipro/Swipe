"""src/services/saved_searches.py."""

import logging
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import ResourceNotFoundError, PermissionDeniedError
from src.models.users import User, SavedSearch
from src.repositories.saved_searches import SavedSearchRepository
from src.schemas.saved_searches import SavedSearchCreate, SavedSearchResponse

logger = logging.getLogger(__name__)


class SavedSearchService:
    """
    Service for managing saved searches.
    """

    def __init__(self, repo: SavedSearchRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_saved_search(
        self, user: User, data: SavedSearchCreate
    ) -> SavedSearchResponse:
        """Saves current filters."""
        saved_search = await self.repo.create(user.id, data)
        await self.session.commit()
        logger.info("User %s saved a new search filter", user.id)
        return saved_search

    async def get_my_searches(self, user: User) -> Sequence[SavedSearchResponse]:
        """Gets a list of the user's saved filters."""
        return await self.repo.get_all_by_user(user.id)

    async def delete_saved_search(self, user: User, search_id: int):
        """Deletes a saved filter."""
        saved_search = await self.repo.get_by_id(search_id)
        if not saved_search:
            raise ResourceNotFoundError()

        if saved_search.user_id != user.id:
            raise PermissionDeniedError()

        await self.repo.delete(saved_search)
        await self.session.commit()
        logger.info("User %s deleted saved search %s", user.id, search_id)
        return {"status": "deleted", "id": search_id}

    async def get_saved_search_by_id(self, user: User, search_id: int) -> SavedSearch:
        """
        Retrieves a single saved search for execution.
        """
        saved_search = await self.repo.get_by_id(search_id)

        if not saved_search:
            raise ResourceNotFoundError()

        if saved_search.user_id != user.id:
            raise PermissionDeniedError()

        return saved_search
