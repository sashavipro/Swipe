"""src/services/admin.py."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.security.password import PasswordHandler
from src.models.real_estate import DealStatus
from src.models.users import User, UserRole
from src.repositories.announcements import AnnouncementRepository
from src.repositories.users import UserRepository
from src.common.exceptions import PermissionDeniedError, ResourceNotFoundError
from src.schemas.real_estate import AnnouncementResponse, AnnouncementReject
from src.schemas.users import (
    UserUpdateByAdmin,
    UserResponse,
    EmployeeCreate,
    ComplaintCreate,
    ComplaintResponse,
)

logger = logging.getLogger(__name__)

PERMISSION_DENIED = "Permission denied"
ONLY_MODERATORS = "Only moderators can perform this action"


class AdminService:
    """Сервис для административных действий (бан, модерация, жалобы)."""

    def __init__(
        self,
        repo: UserRepository,
        announcement_repo: AnnouncementRepository,
        session: AsyncSession,
    ):
        self.repo = repo
        self.announcement_repo = announcement_repo
        self.session = session

    async def get_users(
        self, current_user: User, role: UserRole | None = None
    ) -> list[UserResponse]:
        """
        Вывод всех юзеров.
        Доступно: MODERATOR, NOTARY.
        """
        if current_user.role not in [UserRole.MODERATOR, UserRole.NOTARY]:
            raise PermissionDeniedError(PERMISSION_DENIED)

        return await self.repo.list_users(role=role)

    async def create_user_by_moderator(
        self, moderator: User, data: EmployeeCreate
    ) -> UserResponse:
        """
        Создать пользователя (User, Notary, Moderator).
        """
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError(ONLY_MODERATORS)

        hashed_password = PasswordHandler.get_password_hash(data.password)
        new_user = await self.repo.create_user(data, hashed_password, role=data.role)
        await self.session.commit()

        logger.info("User %s created by moderator %s", new_user.id, moderator.id)
        return new_user

    async def update_user_by_moderator(
        self, moderator: User, user_id: int, data: UserUpdateByAdmin
    ) -> UserResponse:
        """Редактирование пользователя."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError(ONLY_MODERATORS)

        target_user = await self.repo.get_by_id(user_id)
        if not target_user:
            raise ResourceNotFoundError(f"User {user_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        updated_user = await self.repo.update_user(target_user, update_data)
        await self.session.commit()
        return updated_user

    async def delete_user_by_moderator(self, moderator: User, user_id: int):
        """Удаление пользователя."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError(ONLY_MODERATORS)

        if moderator.id == user_id:
            raise PermissionDeniedError("You cannot delete yourself")

        target_user = await self.repo.get_by_id(user_id)
        if not target_user:
            raise ResourceNotFoundError(f"User {user_id} not found")

        await self.repo.delete_user(target_user)
        await self.session.commit()
        return {"status": "deleted", "user_id": user_id}

    async def ban_user(self, moderator: User, user_id: int):
        """Блокировка пользователя."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError("Only moderators can ban users")

        if moderator.id == user_id:
            raise PermissionDeniedError("You cannot ban yourself")

        target_user = await self.repo.get_by_id(user_id)
        if not target_user:
            raise ResourceNotFoundError(f"User {user_id} not found")

        await self.repo.add_to_blacklist(moderator.id, user_id)
        await self.session.commit()
        return {"status": "banned", "user_id": user_id}

    async def unban_user(self, moderator: User, user_id: int):
        """Разблокировка пользователя."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError("Only moderators can unban users")

        await self.repo.remove_from_blacklist(user_id)
        await self.session.commit()
        return {"status": "unbanned", "user_id": user_id}

    async def report_user(
        self, reporter: User, data: ComplaintCreate
    ) -> ComplaintResponse:
        """Пожаловаться на пользователя (доступно всем)."""
        if reporter.id == data.reported_user_id:
            raise PermissionDeniedError("You cannot report yourself")

        target = await self.repo.get_by_id(data.reported_user_id)
        if not target:
            raise ResourceNotFoundError("Reported user not found")

        complaint = await self.repo.create_complaint(reporter.id, data)
        await self.session.commit()
        return complaint

    async def get_complaints(self, moderator: User) -> list[ComplaintResponse]:
        """Просмотр жалоб (только Модератор)."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError("Only moderators can view complaints")

        return await self.repo.list_complaints(resolved=False)

    async def resolve_complaint(self, moderator: User, complaint_id: int):
        """Закрыть жалобу (только Модератор)."""
        if moderator.role != UserRole.MODERATOR:
            raise PermissionDeniedError(PERMISSION_DENIED)

        await self.repo.resolve_complaint(complaint_id)
        await self.session.commit()
        return {"status": "resolved"}

    async def get_pending_announcements(
        self, moderator: User
    ) -> list[AnnouncementResponse]:
        """Получить объявления, ожидающие модерации."""
        if moderator.role not in [UserRole.MODERATOR]:
            raise PermissionDeniedError(
                "Only moderators can view pending announcements"
            )

        return await self.announcement_repo.get_announcements(status=DealStatus.PENDING)

    async def approve_announcement(self, moderator: User, announcement_id: int):
        """Одобрить объявление."""
        if moderator.role not in [UserRole.MODERATOR]:
            raise PermissionDeniedError(PERMISSION_DENIED)

        announcement = await self.announcement_repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError("Announcement not found")

        await self.announcement_repo.change_status(announcement, DealStatus.ACTIVE)
        await self.session.commit()
        return {"status": "approved", "id": announcement_id}

    async def reject_announcement(
        self, moderator: User, announcement_id: int, data: AnnouncementReject
    ):
        """Отклонить объявление."""
        if moderator.role not in [UserRole.MODERATOR]:
            raise PermissionDeniedError(PERMISSION_DENIED)

        announcement = await self.announcement_repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError("Announcement not found")

        await self.announcement_repo.change_status(
            announcement, DealStatus.REJECTED, rejection_reason=data.reason
        )
        await self.session.commit()
        return {"status": "rejected", "id": announcement_id}
