"""src/apps/users/services/saved_searches.py."""

import logging
from typing import Sequence, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.announcements.schemas.announcement import AnnouncementFilter
from src.apps.users.models import User, SavedSearch
from src.apps.users.repositories.saved_searches import SavedSearchRepository
from src.apps.users.schemas.saved_searches import SavedSearchCreate, SavedSearchResponse
from src.core.enum import DealStatus, RoomCount
from src.core.exceptions import ResourceNotFoundError, PermissionDeniedError

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

    def build_filter_from_saved(self, saved_search: SavedSearch) -> AnnouncementFilter:
        """
        Converts a SavedSearch database model into an AnnouncementFilter schema.
        """
        search_data: dict[str, Any] = {}

        for k, v in saved_search.__dict__.items():
            if k.startswith("_"):
                continue

            if k == "status_house":
                continue

            if k == "number_of_rooms" and v is not None:
                val_str = str(v)
                valid_values = {item.value for item in RoomCount}
                if val_str in valid_values:
                    search_data[k] = val_str
                continue

            if k in AnnouncementFilter.model_fields.keys():
                search_data[k] = v

        filter_params = AnnouncementFilter(**search_data)

        if not filter_params.status_house:
            filter_params.status_house = DealStatus.ACTIVE

        return filter_params
