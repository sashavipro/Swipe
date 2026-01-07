"""src/container_factory.py."""

from dishka import make_async_container
from src.infrastructure.provider import InfraProvider
from src.apps.auth.provider import AuthProvider
from src.apps.users.provider import UsersProvider
from src.apps.buildings.provider import BuildingsProvider
from src.apps.announcements.provider import AnnouncementsProvider
from src.apps.admin.provider import AdminProvider


def create_container():
    """
    Container factory.
    Assembles all providers.
    """
    return make_async_container(
        InfraProvider(),
        AuthProvider(),
        UsersProvider(),
        BuildingsProvider(),
        AnnouncementsProvider(),
        AdminProvider(),
    )
