from typing import AsyncIterable

from dishka import Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.database import async_engine, async_session_factory
from src.infrastructure.storage import ImageStorage

# from src.repositories.users import UserRepository
# from src.services.users import UserService


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
        self, engine: AsyncEngine
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

    # @provide(scope=Scope.REQUEST)
    # async def get_user_repo(self, session: AsyncSession) -> UserRepository:
    #     return UserRepository(session)

    # @provide(scope=Scope.REQUEST)
    # async def get_user_service(self, repo: UserRepository) -> UserService:
    #     return UserService(repo)


def make_container():
    """Фабрика контейнера для main.py"""
    container = make_async_container(AppProvider())
    return container
