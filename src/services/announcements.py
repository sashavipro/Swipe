"""src/services/announcements.py."""

import asyncio
import base64
import binascii
import io
import logging
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import (
    ResourceNotFoundError,
    PermissionDeniedError,
    BadRequestError,
)
from src.infrastructure.storage import ImageStorage
from src.models import User
from src.models.real_estate import DealStatus, Image, Announcement
from src.models.users import UserRole
from src.repositories.announcements import AnnouncementRepository
from src.schemas.real_estate import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
    AnnouncementFilter,
    ImageUpdateItem,
)
from src.common.utils import extract_public_id_for_image

logger = logging.getLogger(__name__)


class AnnouncementService:
    """
    Service for working with announcements.
    Responsible for business logic: image processing, rights checking, and orchestration.
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
        """Helper method for processing and uploading an image."""
        # 1. Validation & Decoding
        # Errors here (BadRequestError) should propagate to the user
        try:
            if ";base64," in image_str:
                _, encoded = image_str.split(";base64,")
            else:
                encoded = image_str

            decoded_bytes = base64.b64decode(encoded)
        except (binascii.Error, ValueError) as e:
            logger.warning(
                "Invalid base64 string for user %s at index %s: %s",
                user_id,
                index,
                e,
            )
            raise BadRequestError() from e

        # 2. Uploading
        # Unexpected errors here should be logged, and we skip the image (return None)
        try:
            file_obj = io.BytesIO(decoded_bytes)
            file_obj.name = f"upload_{user_id}_{index}.jpg"

            url = await self.storage.upload_file(file_obj, folder="real_estate")
            return url
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error uploading image index %s for user %s: %s", index, user_id, e
            )
            return None

    async def _process_image_with_index(self, index: int, image_str: str, user_id: int):
        """Wrapper to return index with url."""
        url = await self._process_image(index, image_str, user_id)
        return index, url

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate
    ) -> AnnouncementResponse:
        """Creates an announcement with image upload."""
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
        """Retrieves a list of announcements."""
        return await self.repo.get_announcements(
            status=DealStatus.ACTIVE, limit=limit, offset=offset
        )

    async def _prepare_final_images_list(
        self,
        images_input: list[ImageUpdateItem],
        db_images_map: dict[int, Image],
        user_id: int,
    ) -> tuple[list[Optional[Image]], set[int]]:
        """
        Prepares the final list of images and tasks for uploading new ones.
        Returns: (final_list_with_gaps, kept_image_ids)
        """
        final_images_list = [None] * len(images_input)
        kept_image_ids = set()
        upload_tasks = []

        for i, item in enumerate(images_input):
            if item.id is not None:
                if item.id in db_images_map:
                    img_obj = db_images_map[item.id]
                    img_obj.position = i
                    final_images_list[i] = img_obj
                    kept_image_ids.add(item.id)
                else:
                    logger.warning(
                        "Image ID %s not found in announcement, skipping", item.id
                    )
            elif item.content:
                upload_tasks.append(
                    self._process_image_with_index(i, item.content, user_id)
                )

        if upload_tasks:
            results = await asyncio.gather(*upload_tasks)
            for idx, url in results:
                if url:
                    new_img = Image(image_url=url, position=idx)
                    final_images_list[idx] = new_img

        return final_images_list, kept_image_ids

    async def _handle_images_update(
        self,
        announcement: Announcement,
        images_input: list[ImageUpdateItem],
        user_id: int,
    ) -> list[Image]:
        """
        Processes the image list during an update.
        """
        db_images_map = {img.id: img for img in announcement.images}

        final_images_list, kept_image_ids = await self._prepare_final_images_list(
            images_input, db_images_map, user_id
        )

        valid_images = [img for img in final_images_list if img is not None]

        cleanup_tasks = []
        for img_id, img_obj in db_images_map.items():
            if img_id not in kept_image_ids:
                public_id = extract_public_id_for_image(img_obj.image_url)
                if public_id:
                    cleanup_tasks.append(self.storage.delete_file(public_id))

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        return valid_images

    async def update_announcement(
        self, user: User, announcement_id: int, data: AnnouncementUpdate
    ) -> AnnouncementResponse:
        """Updates an announcement."""
        announcement = await self.repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )
        if not announcement:
            raise ResourceNotFoundError()

        is_owner = announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise PermissionDeniedError()

        update_data = data.model_dump(exclude_unset=True)

        if "images" in update_data:
            images_input = data.images
            del update_data["images"]
            updated_images_list = await self._handle_images_update(
                announcement, images_input, user.id
            )
            announcement.images = updated_images_list

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
        """Deletes an announcement."""
        announcement = await self.repo.get_announcement_by_criteria(
            announcement_id=announcement_id, apartment_id=apartment_id
        )
        if not announcement:
            raise ResourceNotFoundError()

        is_owner = announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise PermissionDeniedError()

        if announcement.images:
            for img in announcement.images:
                public_id = extract_public_id_for_image(img.image_url)
                if public_id:
                    await self.storage.delete_file(public_id)

        await self.repo.delete_announcement(announcement)
        await self.session.commit()

        logger.info("Announcement %s deleted by user %s", announcement.id, user.id)
        return {"status": "deleted", "id": announcement.id}

    async def search_announcements(
        self, filter_params: AnnouncementFilter, limit: int = 20, offset: int = 0
    ) -> Sequence[AnnouncementResponse]:
        """
        Searches announcements by filter.
        """
        if (
            filter_params.price_from
            and filter_params.price_to
            and filter_params.price_from > filter_params.price_to
        ):
            logger.warning("Price range invalid: from > to")
            raise BadRequestError()

        if (
            filter_params.area_from
            and filter_params.area_to
            and filter_params.area_from > filter_params.area_to
        ):
            logger.warning("Area range invalid: from > to")
            raise BadRequestError()

        return await self.repo.search_announcements(filter_params, limit, offset)
