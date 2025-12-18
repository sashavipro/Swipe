"""src/container.py."""

from typing import AsyncIterable

from dishka import Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.database import async_engine, async_session_factory
from src.infrastructure.storage import ImageStorage

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


class AppProvider(Provider):
    """
    Главный провайдер зависимостей.
    Здесь мы учим Dishka создавать объекты.
    """

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        """Возвращаем уже созданный движок из database.py"""
        return async_engine

    @provide(scope=Scope.APP)
    def get_session_factory(
        self, _engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Возвращаем фабрику сессий"""
        return async_session_factory

    @provide(scope=Scope.APP)
    def get_image_storage(self) -> ImageStorage:
        """Сервис загрузки картинок (Cloudinary)"""
        return ImageStorage()

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """
        Создает сессию БД для текущего запроса.
        Автоматически закрывает её (close) после завершения запроса.
        """
        async with session_factory() as session:
            yield session

    # --- REPOSITORIES ---
    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        """Создает репозиторий пользователей."""
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_house_repository(self, session: AsyncSession) -> HouseRepository:
        """Создает репозиторий структуры дома."""
        return HouseRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_announcement_repository(
        self, session: AsyncSession
    ) -> AnnouncementRepository:
        """Создает репозиторий объявлений."""
        return AnnouncementRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_promotion_repository(self, session: AsyncSession) -> PromotionRepository:
        """Создает репозиторий продвижений."""
        return PromotionRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_subscription_repository(
        self, session: AsyncSession
    ) -> SubscriptionRepository:
        """Создает репозиторий подписок."""
        return SubscriptionRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_favorite_repository(self, session: AsyncSession) -> FavoriteRepository:
        """Создает репозиторий избранных."""
        return FavoriteRepository(session)

    # --- SERVICES ---
    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self, repo: UserRepository, session: AsyncSession
    ) -> AuthService:
        """Создает сервис аутентификации."""
        return AuthService(repo, session)

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
        self, repo: PromotionRepository, session: AsyncSession
    ) -> PromotionService:
        """Создает сервис продвижений."""
        return PromotionService(repo, session)

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


def make_container():
    """Фабрика контейнера для main.py"""
    container = make_async_container(AppProvider())
    return container
