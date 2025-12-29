"""src/infrastructure/providers/repositories.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.chessboard import ChessboardRepository
from src.repositories.saved_searches import SavedSearchRepository
from src.repositories.users import UserRepository
from src.repositories.houses import HouseRepository
from src.repositories.announcements import AnnouncementRepository
from src.repositories.promotions import PromotionRepository
from src.repositories.subscriptions import SubscriptionRepository
from src.repositories.favorites import FavoriteRepository


class RepositoryProvider(Provider):
    """
    Data access layer provider (Repositories).
    All repositories depend on AsyncSession.
    """

    scope = Scope.REQUEST

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        """Creates user repository."""
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_house_repository(self, session: AsyncSession) -> HouseRepository:
        """Creates house repository."""
        return HouseRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_announcement_repository(
        self, session: AsyncSession
    ) -> AnnouncementRepository:
        """Creates announcement repository."""
        return AnnouncementRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_promotion_repository(self, session: AsyncSession) -> PromotionRepository:
        """Creates promotion repository."""
        return PromotionRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_subscription_repository(
        self, session: AsyncSession
    ) -> SubscriptionRepository:
        """Creates subscription repository."""
        return SubscriptionRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_favorite_repository(self, session: AsyncSession) -> FavoriteRepository:
        """Creates favorite repository."""
        return FavoriteRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_chessboard_repository(self, session: AsyncSession) -> ChessboardRepository:
        """Creates chessboard request repository."""
        return ChessboardRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_saved_search_repository(
        self, session: AsyncSession
    ) -> SavedSearchRepository:
        """Creates saved search repository."""
        return SavedSearchRepository(session)
