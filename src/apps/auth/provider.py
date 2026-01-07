"""src/apps/auth/provider.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from src.apps.auth.repositories import AuthRepository
from src.apps.auth.services import AuthService
from src.apps.users.repositories.user_profile import UserRepository


class AuthProvider(Provider):
    """
    Dishka provider for the Authentication module.
    Manages security, identity, and verification dependencies.
    """

    scope = Scope.REQUEST

    @provide
    def auth_repo(self, session: AsyncSession) -> AuthRepository:
        """
        Provides an AuthRepository instance for handling verification codes.
        """
        return AuthRepository(session)

    @provide
    def auth_service(
        self,
        user_repo: UserRepository,
        auth_repo: AuthRepository,
        session: AsyncSession,
        redis: Redis,
    ) -> AuthService:
        """
        Provides an AuthService instance for registration and token management.
        """
        return AuthService(
            user_repo=user_repo, auth_repo=auth_repo, session=session, redis=redis
        )
