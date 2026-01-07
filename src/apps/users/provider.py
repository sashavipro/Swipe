"""src/apps/users/provider.py."""

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.users.repositories.user_profile import UserRepository
from src.apps.users.repositories.subscription import SubscriptionRepository
from src.apps.users.repositories.favorite import FavoriteRepository
from src.apps.users.repositories.complaint import ComplaintRepository
from src.apps.users.repositories.saved_searches import SavedSearchRepository
from src.apps.users.repositories.chat import ChatRepository
from src.apps.users.services.user_profile import UserProfileService
from src.apps.users.services.subscription import SubscriptionService
from src.apps.users.services.favorite import FavoriteService
from src.apps.users.services.complaint import ComplaintService
from src.apps.users.services.saved_searches import SavedSearchService
from src.apps.users.services.chat import ChatService
from src.infrastructure.storage import ImageStorage


class UsersProvider(Provider):
    """
    Dishka provider for the Users module.
    Aggregates profile management, social features, and subscription dependencies.
    """

    scope = Scope.REQUEST

    # --- Repositories ---

    @provide
    def user_repo(self, session: AsyncSession) -> UserRepository:
        """Provides a UserRepository instance."""
        return UserRepository(session)

    @provide
    def subscription_repo(self, session: AsyncSession) -> SubscriptionRepository:
        """Provides a SubscriptionRepository instance."""
        return SubscriptionRepository(session)

    @provide
    def favorite_repo(self, session: AsyncSession) -> FavoriteRepository:
        """Provides a FavoriteRepository instance."""
        return FavoriteRepository(session)

    @provide
    def complaint_repo(self, session: AsyncSession) -> ComplaintRepository:
        """Provides a ComplaintRepository instance."""
        return ComplaintRepository(session)

    @provide
    def saved_search_repo(self, session: AsyncSession) -> SavedSearchRepository:
        """Provides a SavedSearchRepository instance."""
        return SavedSearchRepository(session)

    @provide
    def chat_repo(self, session: AsyncSession) -> ChatRepository:
        """Provides a ChatRepository instance."""
        return ChatRepository(session)

    # --- Services ---

    @provide
    def user_profile_service(
        self, repo: UserRepository, storage: ImageStorage, session: AsyncSession
    ) -> UserProfileService:
        """ "Provides a UserProfileService instance for profile and avatar management."""
        return UserProfileService(repo=repo, storage=storage, session=session)

    @provide
    def subscription_service(
        self, repo: SubscriptionRepository, session: AsyncSession
    ) -> SubscriptionService:
        """Provides a SubscriptionService instance for plan management."""
        return SubscriptionService(repo=repo, session=session)

    @provide
    def favorite_service(
        self, repo: FavoriteRepository, session: AsyncSession
    ) -> FavoriteService:
        """Provides a FavoriteService instance for managing user bookmarks."""
        return FavoriteService(repo=repo, session=session)

    @provide
    def complaint_service(
        self,
        repo: ComplaintRepository,
        repo_user: UserRepository,
        session: AsyncSession,
    ) -> ComplaintService:
        """Provides a ComplaintService instance for reporting and moderation."""
        return ComplaintService(repo=repo, repo_user=repo_user, session=session)

    @provide
    def saved_search_service(
        self, repo: SavedSearchRepository, session: AsyncSession
    ) -> SavedSearchService:
        """Provides a SavedSearchService instance for persistent search filters."""
        return SavedSearchService(repo=repo, session=session)

    @provide
    def chat_service(
        self,
        repo: ChatRepository,
        user_repo: UserRepository,
        storage: ImageStorage,
        session: AsyncSession,
    ) -> ChatService:
        """Provides a ChatService instance."""
        return ChatService(
            repo=repo, user_repo=user_repo, storage=storage, session=session
        )
