"""src/apps/buildings/provider.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.buildings.repositories import HouseRepository
from src.apps.buildings.services import HouseService
from src.infrastructure.storage import ImageStorage


class BuildingsProvider(Provider):
    """
    Dishka provider for the Buildings module.
    Responsible for real estate catalog and structural data dependencies.
    """

    scope = Scope.REQUEST

    @provide
    def house_repository(self, session: AsyncSession) -> HouseRepository:
        """
        Provides a HouseRepository instance for real estate data access.
        """
        return HouseRepository(session)

    @provide
    def house_service(
        self, repo: HouseRepository, session: AsyncSession, storage: ImageStorage
    ) -> HouseService:
        """
        Provides a HouseService instance for managing complex buildings, news, and documents.
        """
        return HouseService(repo=repo, session=session, storage=storage)
