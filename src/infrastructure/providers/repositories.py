"""src/infrastructure/providers/repositories.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.chessboard import ChessboardRepository
from src.repositories.users import UserRepository
from src.repositories.houses import HouseRepository
from src.repositories.announcements import AnnouncementRepository
from src.repositories.promotions import PromotionRepository
from src.repositories.subscriptions import SubscriptionRepository
from src.repositories.favorites import FavoriteRepository


class RepositoryProvider(Provider):
    """
    Провайдер слоя доступа к данным (Repositories).
    Все репозитории зависят от AsyncSession.
    """

    scope = Scope.REQUEST

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

    @provide(scope=Scope.REQUEST)
    def get_chessboard_repository(self, session: AsyncSession) -> ChessboardRepository:
        """Создает репозиторий заявок в шахматку."""
        return ChessboardRepository(session)
