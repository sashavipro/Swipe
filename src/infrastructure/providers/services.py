"""src/infrastructure/providers/services.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.infrastructure.storage import ImageStorage
from src.repositories.saved_searches import SavedSearchRepository
from src.services.admin import AdminService

from src.services.auth import AuthService
from src.services.houses import HouseService
from src.services.announcements import AnnouncementService
from src.services.promotions import PromotionService
from src.services.saved_searches import SavedSearchService
from src.services.user_profile import UserProfileService
from src.services.subscriptions import SubscriptionService
from src.services.favorites import FavoriteService
from src.services.chessboard import ChessboardService

from src.repositories.users import UserRepository
from src.repositories.houses import HouseRepository
from src.repositories.announcements import AnnouncementRepository
from src.repositories.promotions import PromotionRepository
from src.repositories.subscriptions import SubscriptionRepository
from src.repositories.favorites import FavoriteRepository
from src.repositories.chessboard import ChessboardRepository


class ServiceProvider(Provider):
    """
    Business logic layer provider (Services).
    """

    scope = Scope.REQUEST

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self, repo: UserRepository, session: AsyncSession, redis: Redis
    ) -> AuthService:
        """Creates authentication service."""
        return AuthService(repo, session, redis)

    @provide(scope=Scope.REQUEST)
    def get_house_service(
        self, repo: HouseRepository, session: AsyncSession, storage: ImageStorage
    ) -> HouseService:
        """Creates house service."""
        return HouseService(repo, session, storage)

    @provide(scope=Scope.REQUEST)
    def get_announcement_service(
        self,
        repo: AnnouncementRepository,
        session: AsyncSession,
        storage: ImageStorage,
    ) -> AnnouncementService:
        """Creates announcement service."""
        return AnnouncementService(repo, session, storage)

    @provide(scope=Scope.REQUEST)
    def get_promotion_service(
        self,
        repo: PromotionRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> PromotionService:
        """Creates promotion service."""
        return PromotionService(repo, announcement_repo, session)

    @provide(scope=Scope.REQUEST)
    def get_user_profile_service(
        self, repo: UserRepository, session: AsyncSession, storage: ImageStorage
    ) -> UserProfileService:
        """Creates user profile service."""
        return UserProfileService(repo, session, storage)

    @provide(scope=Scope.REQUEST)
    def get_subscription_service(
        self, repo: SubscriptionRepository, session: AsyncSession
    ) -> SubscriptionService:
        """Creates subscription service."""
        return SubscriptionService(repo, session)

    @provide(scope=Scope.REQUEST)
    def get_favorite_service(
        self, repo: FavoriteRepository, session: AsyncSession
    ) -> FavoriteService:
        """Creates favorite service."""
        return FavoriteService(repo, session)

    @provide(scope=Scope.REQUEST)
    def get_admin_service(
        self,
        repo: UserRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> AdminService:
        """Creates admin service."""
        return AdminService(repo, announcement_repo, session)

    @provide(scope=Scope.REQUEST)
    def get_chessboard_service(
        self,
        repo: ChessboardRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> ChessboardService:
        """Creates chessboard service."""
        return ChessboardService(repo, announcement_repo, session)

    @provide(scope=Scope.REQUEST)
    def get_saved_search_service(
        self, repo: SavedSearchRepository, session: AsyncSession
    ) -> SavedSearchService:
        """Creates saved search service."""
        return SavedSearchService(repo, session)
