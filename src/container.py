"""src/container.py."""

from dishka import make_async_container

from src.infrastructure.providers.base import InfraProvider
from src.infrastructure.providers.repositories import RepositoryProvider
from src.infrastructure.providers.services import ServiceProvider


def make_container():
    """
    Container factory.
    Assembles all providers (Infrastructure, Repositories, Services).
    """
    container = make_async_container(
        InfraProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )

    return container
