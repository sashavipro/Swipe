"""src/services/real_estate.py."""

import base64
import io
import re
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.infrastructure.storage import ImageStorage
from src.models import User
from src.models.users import UserRole
from src.repositories.real_estate import RealEstateRepository
from src.schemas.real_estate import (
    HouseCreate,
    HouseResponse,
    AnnouncementCreate,
    AnnouncementResponse,
    PromotionCreate,
    PromotionResponse,
    AnnouncementUpdate,
    PromotionUpdate,
)


class RealEstateService:
    """
    Сервис для работы с недвижимостью.
    """

    def __init__(
        self, repo: RealEstateRepository, session: AsyncSession, storage: ImageStorage
    ):
        self.repo = repo
        self.session = session
        self.storage = storage

    async def create_house(self, data: HouseCreate) -> HouseResponse:
        """
        Создает ЖК со всей структурой.
        """
        house = await self.repo.create_house(data)
        await self.session.commit()
        return house

    async def get_houses(self) -> Sequence[HouseResponse]:
        """
        Возвращает список всех ЖК.
        """
        return await self.repo.get_all_houses()

    async def create_promotion(
        self, user: User, announcement_id: int, data: PromotionCreate
    ) -> PromotionResponse:
        """Создать продвижение для объявления."""
        check_user_id = user.id
        if user.role in [UserRole.MODERATOR, UserRole.AGENT]:
            check_user_id = None

        promo = await self.repo.create_promotion(announcement_id, data, check_user_id)

        await self.session.commit()
        return promo

    async def create_announcement(
        self, user_id: int, data: AnnouncementCreate
    ) -> AnnouncementResponse:
        """
        Загрузка Base64 картинок в Cloudinary и создание объявления.
        """
        image_urls = []

        for i, image_str in enumerate(data.images):
            try:
                if ";base64," in image_str:
                    _, encoded = image_str.split(";base64,")
                else:
                    encoded = image_str

                decoded_bytes = base64.b64decode(encoded)

                file_obj = io.BytesIO(decoded_bytes)
                file_obj.name = f"upload_{user_id}_{i}.jpg"

                url = await self.storage.upload_file(file_obj, folder="real_estate")
                image_urls.append(url)
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Error processing image {i}: {e}")
                continue

        announcement = await self.repo.create_announcement(user_id, data, image_urls)

        await self.session.commit()
        return announcement

    async def get_announcements(self) -> Sequence[AnnouncementResponse]:
        """Получить список всех объявлений."""
        return await self.repo.get_announcements()

    def _extract_public_id(self, image_url: str) -> str | None:
        """
        Извлекает public_id из ссылки Cloudinary.
        """
        if not image_url:
            return None

        match = re.search(r"(swipe_project/.*)\.", image_url)
        if match:
            return match.group(1)
        return None

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found"
            )

        is_owner = announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this announcement",
            )

        if announcement.images:
            for img in announcement.images:
                public_id = self._extract_public_id(img.image_url)
                if public_id:
                    await self.storage.delete_file(public_id)

        await self.repo.delete_announcement(announcement)
        await self.session.commit()

        return {"status": "deleted", "id": announcement.id}

    async def delete_promotion(self, user: User, promotion_id: int):
        """
        Удаляет продвижение.
        """
        promotion = await self.repo.get_promotion_by_id(promotion_id)

        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found"
            )

        is_owner = promotion.announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this promotion",
            )

        await self.repo.delete_promotion(promotion)
        await self.session.commit()

        return {"status": "deleted", "id": promotion_id}

    async def update_announcement(
        self, user: User, announcement_id: int, data: AnnouncementUpdate
    ) -> AnnouncementResponse:
        """
        Обновляет объявление.
        """
        announcement = await self.repo.get_announcement_by_criteria(
            announcement_id=announcement_id
        )

        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        is_owner = announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        update_data = data.model_dump(exclude_unset=True)

        updated_announcement = await self.repo.update_announcement(
            announcement, update_data
        )
        await self.session.commit()

        return updated_announcement

    async def update_promotion(
        self, user: User, promotion_id: int, data: PromotionUpdate
    ) -> PromotionResponse:
        """
        Обновляет продвижение.
        """
        promotion = await self.repo.get_promotion_by_id(promotion_id)

        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion not found")

        is_owner = promotion.announcement.user_id == user.id
        is_admin = user.role in [UserRole.MODERATOR, UserRole.AGENT]

        if not is_owner and not is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        update_data = data.model_dump(exclude_unset=True)

        updated_promo = await self.repo.update_promotion(promotion, update_data)
        await self.session.commit()

        return updated_promo
