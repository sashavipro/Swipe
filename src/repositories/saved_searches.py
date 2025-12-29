"""src/repositories/saved_searches.py."""

import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import SavedSearch
from src.schemas.saved_searches import SavedSearchCreate

logger = logging.getLogger(__name__)


class SavedSearchRepository:
    """
    Repository for working with user's saved filters.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, data: SavedSearchCreate) -> SavedSearch:
        """Creates a new saved search."""
        saved_search = SavedSearch(user_id=user_id, **data.model_dump())
        self.session.add(saved_search)
        await self.session.flush()
        return saved_search

    async def get_all_by_user(self, user_id: int) -> Sequence[SavedSearch]:
        """Returns all saved searches of the user."""
        stmt = (
            select(SavedSearch)
            .where(SavedSearch.user_id == user_id)
            .order_by(SavedSearch.id.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, search_id: int) -> SavedSearch | None:
        """Retrieves a search by ID."""
        stmt = select(SavedSearch).where(SavedSearch.id == search_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, saved_search: SavedSearch) -> None:
        """Deletes a saved search."""
        await self.session.delete(saved_search)
        await self.session.flush()
