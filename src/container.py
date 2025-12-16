"""src/container.py."""

from typing import AsyncIterable

from dishka import Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.database import async_engine, async_session_factory
from src.infrastructure.storage import ImageStorage
from src.repositories.real_estate import RealEstateRepository

from src.repositories.users import UserRepository
from src.services.auth import AuthService
from src.services.real_estate import RealEstateService
from src.services.users import UserService


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

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        """Создает репозиторий пользователей."""
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self, repo: UserRepository, session: AsyncSession
    ) -> AuthService:
        """Создает сервис аутентификации."""
        return AuthService(repo, session)

    @provide(scope=Scope.REQUEST)
    def get_real_estate_repo(self, session: AsyncSession) -> RealEstateRepository:
        """Создает репозиторий недвижимости."""
        return RealEstateRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_real_estate_service(
        self, repo: RealEstateRepository, session: AsyncSession
    ) -> RealEstateService:
        """Создает сервис недвижимости."""
        return RealEstateService(repo, session)

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self, repo: UserRepository, session: AsyncSession, storage: ImageStorage
    ) -> UserService:
        """Создает сервис пользователей."""
        return UserService(repo, session, storage)


def make_container():
    """Фабрика контейнера для main.py"""
    container = make_async_container(AppProvider())
    return container
