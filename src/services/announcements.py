"""src/services/announcements.py."""

import asyncio
import base64
import io
import logging
import re
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import ResourceNotFoundError, PermissionDeniedError
from src.infrastructure.storage import ImageStorage
from src.models import User
from src.models.real_estate import DealStatus
from src.models.users import UserRole
from src.repositories.announcements import AnnouncementRepository
from src.schemas.real_estate import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
)

logger = logging.getLogger(__name__)


class AnnouncementService:
    """
    Сервис для работы с объявлениями.
    Отвечает за бизнес-логику: обработку изображений, проверку прав и оркестрацию.
    """

    def __init__(
        self, repo: AnnouncementRepository, session: AsyncSession, storage: ImageStorage
    ):
        self.repo = repo
        self.session = session
        self.storage = storage

    async def _process_image(
        self, index: int, image_str: str, user_id: int
    ) -> str | None:
        """
        Вспомогательный метод для обработки и загрузки одного изображения.
        Возвращает URL или None в случае ошибки.
        """
        try:
            if ";base64," in image_str:
                _, encoded = image_str.split(";base64,")
            else:
                encoded = image_str

            decoded_bytes = base64.b64decode(encoded)
            file_obj = io.BytesIO(decoded_bytes)
            file_obj.name = f"upload_{user_id}_{index}.jpg"

            url = await self.storage.upload_file(file_obj, folder="real_estate")
            return url

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error processing image index %s for user %s: %s", index, user_id, e
            )
            return None

    def _extract_public_id(self, image_url: str) -> str | None:
        """
        Извлекает public_id из ссылки Cloudinary.
        Пример: https://res.cloudinary.com/.../swipe_project/real_estate/xyz.jpg
        -> swipe_project/real_estate/xyz
        """
        if not image_url:
            return None

        match = re.search(r"(swipe_project/.*)\.", image_url)
        if match:
            return match.group(1)
        return None

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate
    ) -> AnnouncementResponse:
        """
        Загрузка Base64 картинок в Cloudinary (параллельно) и создание объявления.
        Реализован механизм компенсации (удаления фото) при ошибке БД.
        """
        logger.info("Starting announcement creation for user_id=%s", user_id)

        upload_tasks = [
            self._process_image(i, img_str, user_id)
            for i, img_str in enumerate(data.images)
        ]
        results = await asyncio.gather(*upload_tasks)

        image_urls = [url for url in results if url is not None]

        logger.info(
            "Images processed: %d uploaded successfully out of %d",
            len(image_urls),
            len(data.images),
        )

        try:
            announcement = await self.repo.create_announcement(
                user_id, data, image_urls
            )
            await self.session.commit()

            logger.info("Announcement created successfully: id=%s", announcement.id)
            return announcement

        except Exception as e:
            logger.error(
                "Database error during announcement creation: %s. "
                "Rolling back Cloudinary uploads...",
                e,
            )

            if image_urls:
                cleanup_tasks = []
                for url in image_urls:
                    public_id = self._extract_public_id(url)
                    if public_id:
                        cleanup_tasks.append(self.storage.delete_file(public_id))

                if cleanup_tasks:
                    await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                    logger.info(
                        "Rollback complete: Deleted orphaned images from Cloudinary."
                    )
            raise e

    async def get_announcements(
        self, limit: int = 20, offset: int = 0
    ) -> Sequence[AnnouncementResponse]:
        """Получить список всех объявлений с пагинацией."""
        return await self.repo.get_announcements(
            status=DealStatus.ACTIVE, limit=limit, offset=offset
        )

    async def update_announcement(
        self, user: User, announcement_id: int, data: AnnouncementUpdate
    ) -> AnnouncementResponse:
        """
        Обновляет объявление.
        Если обновляет владелец -> статус меняется на PENDING (на модерацию).
        Если обновляет модератор -> статус можно менять произвольно.
        """
        announcement = await self.repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
            logger.warning("Update failed: Announcement %s not found", announcement_id)
            raise ResourceNotFoundError(
                f"Announcement with id {announcement_id} not found"
            )

        is_owner = announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise PermissionDeniedError(
                "You do not have permission to update this announcement"
            )

        update_data = data.model_dump(exclude_unset=True)

        if is_owner and not is_admin:
            if "status" in update_data:
                del update_data["status"]

            update_data["status"] = DealStatus.PENDING
            update_data["rejection_reason"] = None

            logger.info(
                "Announcement %s sent to re-moderation after update by owner",
                announcement_id,
            )

        updated_announcement = await self.repo.update_announcement(
            announcement, update_data
        )
        await self.session.commit()

        logger.info("Announcement %s updated successfully", announcement_id)
        return updated_announcement

    async def delete_announcement(
        self,
        user: User,
        announcement_id: int | None = None,
        apartment_id: int | None = None,
    ):
        """
        Удаляет объявление.
        Проверяет, является ли пользователь владельцем.
        """
        announcement = await self.repo.get_announcement_by_criteria(
            announcement_id=announcement_id, apartment_id=apartment_id
        )
        if not announcement:
            logger.warning(
                "Delete failed: Announcement not found (id=%s, apt_id=%s)",
                announcement_id,
                apartment_id,
            )
            raise ResourceNotFoundError("Announcement not found")

        is_owner = announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            logger.warning(
                "Permission denied: User %s tried to delete announcement %s",
                user.id,
                announcement.id,
            )
            raise PermissionDeniedError(
                "You do not have permission to delete this announcement"
            )

        if announcement.images:
            logger.info("Deleting images for announcement %s", announcement.id)
            for img in announcement.images:
                public_id = self._extract_public_id(img.image_url)
                if public_id:
                    await self.storage.delete_file(public_id)

        await self.repo.delete_announcement(announcement)
        await self.session.commit()

        logger.info("Announcement %s deleted by user %s", announcement.id, user.id)
        return {"status": "deleted", "id": announcement.id}
