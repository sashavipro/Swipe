"""src/services/announcements.py."""

import asyncio
import base64
import io
import logging
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import ResourceNotFoundError, PermissionDeniedError
from src.infrastructure.storage import ImageStorage
from src.models import User
from src.models.real_estate import DealStatus, Image, Announcement
from src.models.users import UserRole
from src.repositories.announcements import AnnouncementRepository
from src.schemas.real_estate import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
)
from src.common.utils import extract_public_id_for_image

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
        """Вспомогательный метод для обработки и загрузки."""
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

    async def _process_image_with_index(self, index: int, image_str: str, user_id: int):
        """Обертка для возврата индекса с url."""
        url = await self._process_image(index, image_str, user_id)
        return index, url

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate
    ) -> AnnouncementResponse:
        """Создает объявление с загрузкой изображений."""
        logger.info("Starting announcement creation for user_id=%s", user_id)

        upload_tasks = [
            self._process_image(i, img_str, user_id)
            for i, img_str in enumerate(data.images)
        ]
        results = await asyncio.gather(*upload_tasks)
        image_urls = [url for url in results if url is not None]

        try:
            announcement = await self.repo.create_announcement(
                user_id, data, image_urls
            )
            await self.session.commit()
            logger.info("Announcement created successfully: id=%s", announcement.id)
            return announcement

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Database error. Rolling back Cloudinary uploads: %s", e)
            if image_urls:
                cleanup_tasks = []
                for url in image_urls:
                    public_id = extract_public_id_for_image(url)
                    if public_id:
                        cleanup_tasks.append(self.storage.delete_file(public_id))
                if cleanup_tasks:
                    await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            raise e

    async def get_announcements(
        self, limit: int = 20, offset: int = 0
    ) -> Sequence[AnnouncementResponse]:
        """Получает список объявлений."""
        return await self.repo.get_announcements(
            status=DealStatus.ACTIVE, limit=limit, offset=offset
        )

    async def _prepare_image_objects(
        self,
        new_images_input: list[str],
        current_images_map: dict[str, Image],
        user_id: int,
    ) -> list[Image]:
        """Подготавливает список объектов Image (существующих и новых)."""
        final_image_objects = [None] * len(new_images_input)
        upload_tasks = []

        for i, img_str in enumerate(new_images_input):
            if img_str.startswith("http"):
                if img_str in current_images_map:
                    final_image_objects[i] = current_images_map[img_str]
                else:
                    final_image_objects[i] = Image(image_url=img_str)
            else:
                upload_tasks.append(self._process_image_with_index(i, img_str, user_id))

        if upload_tasks:
            results = await asyncio.gather(*upload_tasks)
            for idx, url in results:
                if url:
                    final_image_objects[idx] = Image(image_url=url)

        return [obj for obj in final_image_objects if obj is not None]

    async def _handle_images_update(
        self,
        announcement: Announcement,
        new_images_input: list[str],
        user_id: int,
    ) -> list[Image]:
        """
        Обрабатывает список изображений при обновлении.
        """
        current_images_map = {img.image_url: img for img in announcement.images}

        valid_image_objects = await self._prepare_image_objects(
            new_images_input, current_images_map, user_id
        )

        # Cleanup removed images
        new_urls_set = {obj.image_url for obj in valid_image_objects}
        cleanup_tasks = []
        for url in current_images_map:
            if url not in new_urls_set:
                public_id = extract_public_id_for_image(url)
                if public_id:
                    cleanup_tasks.append(self.storage.delete_file(public_id))

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        return valid_image_objects

    async def update_announcement(
        self, user: User, announcement_id: int, data: AnnouncementUpdate
    ) -> AnnouncementResponse:
        """
        Обновляет объявление. Сохраняет ID существующих картинок.
        """
        announcement = await self.repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
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

        if "images" in update_data:
            new_images_input = update_data.pop("images")
            update_data["images"] = await self._handle_images_update(
                announcement, new_images_input, user.id
            )

        if is_owner and not is_admin:
            if "status" in update_data:
                del update_data["status"]
            update_data["status"] = DealStatus.PENDING
            update_data["rejection_reason"] = None
            logger.info("Announcement %s sent to re-moderation", announcement_id)

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
        """Удаляет объявление."""
        announcement = await self.repo.get_announcement_by_criteria(
            announcement_id=announcement_id, apartment_id=apartment_id
        )
        if not announcement:
            raise ResourceNotFoundError("Announcement not found")

        is_owner = announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise PermissionDeniedError(
                "You do not have permission to delete this announcement"
            )

        if announcement.images:
            for img in announcement.images:
                public_id = extract_public_id_for_image(img.image_url)
                if public_id:
                    await self.storage.delete_file(public_id)

        await self.repo.delete_announcement(announcement)
        await self.session.commit()

        logger.info("Announcement %s deleted by user %s", announcement.id, user.id)
        return {"status": "deleted", "id": announcement.id}
