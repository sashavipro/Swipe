"""src/container.py."""

from dishka import make_async_container

from src.infrastructure.providers.base import InfraProvider
from src.infrastructure.providers.repositories import RepositoryProvider
from src.infrastructure.providers.services import ServiceProvider


def make_container():
    """
    Фабрика контейнера.
    Собирает все провайдеры (Инфраструктура, Репозитории, Сервисы).
    """
    container = make_async_container(
        InfraProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )

    return container
