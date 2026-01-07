"""src/apps/announcements/provider.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.announcements.repositories.announcement import AnnouncementRepository
from src.apps.announcements.repositories.chessboard import ChessboardRepository
from src.apps.announcements.repositories.promotion import PromotionRepository
from src.apps.announcements.services.announcement import AnnouncementService
from src.apps.announcements.services.chessboard import ChessboardService
from src.apps.announcements.services.promotion import PromotionService
from src.infrastructure.storage import ImageStorage


class AnnouncementsProvider(Provider):
    """
    Dishka provider for the Announcements module.
    Manages dependencies for announcements, promotions, and chessboard features.
    """

    scope = Scope.REQUEST

    # --- Repositories ---

    @provide
    def announcement_repo(self, session: AsyncSession) -> AnnouncementRepository:
        """
        Provides the AnnouncementRepository.
        """
        return AnnouncementRepository(session)

    @provide
    def chessboard_repo(self, session: AsyncSession) -> ChessboardRepository:
        """
        Provides the ChessboardRepository.
        """
        return ChessboardRepository(session)

    @provide
    def promotion_repo(self, session: AsyncSession) -> PromotionRepository:
        """
        Provides the PromotionRepository.
        """
        return PromotionRepository(session)

    # --- Services ---

    @provide
    def announcement_service(
        self,
        repo: AnnouncementRepository,
        session: AsyncSession,
        storage: ImageStorage,
    ) -> AnnouncementService:
        """
        Provides the AnnouncementService.
        """
        return AnnouncementService(repo=repo, session=session, storage=storage)

    @provide
    def chessboard_service(
        self,
        repo: ChessboardRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> ChessboardService:
        """
        Provides the ChessboardService.
        """
        return ChessboardService(
            repo=repo, announcement_repo=announcement_repo, session=session
        )

    @provide
    def promotion_service(
        self,
        repo: PromotionRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> PromotionService:
        """
        Provides the PromotionService.
        """
        return PromotionService(
            repo=repo, announcement_repo=announcement_repo, session=session
        )
