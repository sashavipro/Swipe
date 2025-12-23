"""src/infrastructure/providers/services.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.infrastructure.storage import ImageStorage
from src.services.admin import AdminService

from src.services.auth import AuthService
from src.services.houses import HouseService
from src.services.announcements import AnnouncementService
from src.services.promotions import PromotionService
from src.services.user_profile import UserProfileService
from src.services.subscriptions import SubscriptionService
from src.services.favorites import FavoriteService

from src.repositories.users import UserRepository
from src.repositories.houses import HouseRepository
from src.repositories.announcements import AnnouncementRepository
from src.repositories.promotions import PromotionRepository
from src.repositories.subscriptions import SubscriptionRepository
from src.repositories.favorites import FavoriteRepository


class ServiceProvider(Provider):
    """
    Провайдер слоя бизнес-логики (Services).
    Сервисы зависят от Репозиториев, Сессии и (иногда) Storage.
    """

    scope = Scope.REQUEST

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self, repo: UserRepository, session: AsyncSession, redis: Redis
    ) -> AuthService:
        """Создает сервис аутентификации."""
        return AuthService(repo, session, redis)

    @provide(scope=Scope.REQUEST)
    def get_house_service(
        self, repo: HouseRepository, session: AsyncSession
    ) -> HouseService:
        """Создает сервис дома."""
        return HouseService(repo, session)

    @provide(scope=Scope.REQUEST)
    def get_announcement_service(
        self,
        repo: AnnouncementRepository,
        session: AsyncSession,
        storage: ImageStorage,
    ) -> AnnouncementService:
        """Создает сервис объявлений."""
        return AnnouncementService(repo, session, storage)

    @provide(scope=Scope.REQUEST)
    def get_promotion_service(
        self,
        repo: PromotionRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> PromotionService:
        """Создает сервис продвижений."""
        return PromotionService(repo, announcement_repo, session)

    @provide(scope=Scope.REQUEST)
    def get_user_profile_service(
        self, repo: UserRepository, session: AsyncSession, storage: ImageStorage
    ) -> UserProfileService:
        """Создает сервис пользователей."""
        return UserProfileService(repo, session, storage)

    @provide(scope=Scope.REQUEST)
    def get_subscription_service(
        self, repo: SubscriptionRepository, session: AsyncSession
    ) -> SubscriptionService:
        """Создает сервис подписок."""
        return SubscriptionService(repo, session)

    @provide(scope=Scope.REQUEST)
    def get_favorite_service(
        self, repo: FavoriteRepository, session: AsyncSession
    ) -> FavoriteService:
        """Создает сервис избранных."""
        return FavoriteService(repo, session)

    @provide(scope=Scope.REQUEST)
    def get_admin_service(
        self,
        repo: UserRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> AdminService:
        """Создает сервис для администратора."""
        return AdminService(repo, announcement_repo, session)
