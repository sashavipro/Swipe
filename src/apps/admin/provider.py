"""src/apps/admin/provider.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.admin.repositories.blacklist import BlacklistRepository
from src.apps.admin.repositories.crud_user import CrudUserRepository
from src.apps.admin.services.blacklist import BlacklistService
from src.apps.admin.services.crud_user import CrudUserService
from src.apps.admin.services.moderation_announcement import (
    ModerationAnnouncementService,
)
from src.apps.users.repositories.user_profile import UserRepository
from src.apps.announcements.repositories.announcement import AnnouncementRepository


class AdminProvider(Provider):
    """
    Dishka provider for the Admin module.
    Responsible for injecting administrative repositories and services.
    """

    scope = Scope.REQUEST

    # --- Repositories ---

    @provide
    def blacklist_repo(self, session: AsyncSession) -> BlacklistRepository:
        """
        Provides a BlacklistRepository instance.
        """
        return BlacklistRepository(session)

    @provide
    def crud_user_repo(self, session: AsyncSession) -> CrudUserRepository:
        """
        Provides a CrudUserRepository instance for administrative user management.
        """
        return CrudUserRepository(session)

    # --- Services ---

    @provide
    def blacklist_service(
        self,
        repo: BlacklistRepository,
        repo_user: UserRepository,
        session: AsyncSession,
    ) -> BlacklistService:
        """
        Provides a BlacklistService instance for managing user bans.
        """
        return BlacklistService(repo=repo, repo_user=repo_user, session=session)

    @provide
    def crud_user_service(
        self,
        repo: UserRepository,
        repo_crud_user: CrudUserRepository,
        session: AsyncSession,
    ) -> CrudUserService:
        """
        Provides a CrudUserService instance for administrative user CRUD operations.
        """
        return CrudUserService(
            repo=repo, repo_crud_user=repo_crud_user, session=session
        )

    @provide
    def moderation_service(
        self,
        repo: UserRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ) -> ModerationAnnouncementService:
        """
        Provides a ModerationAnnouncementService instance for managing ad approvals.
        """
        return ModerationAnnouncementService(
            repo=repo, announcement_repo=announcement_repo, session=session
        )
