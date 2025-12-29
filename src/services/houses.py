"""src/services/houses.py."""

import logging
import re
from typing import Sequence
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.houses import HouseRepository
from src.schemas.real_estate import (
    HouseCreate,
    HouseResponse,
    HouseInfoUpdate,
    NewsCreate,
    NewsResponse,
    DocumentResponse,
    DocumentCreate,
)
from src.models.users import User, UserRole
from src.common.exceptions import (
    PermissionDeniedError,
    ResourceNotFoundError,
    BadRequestError,
)
from src.infrastructure.storage import ImageStorage
from src.common.utils import check_owner_or_admin, extract_public_id_for_image

logger = logging.getLogger(__name__)


class HouseService:
    """
    Service for working with houses.
    """

    def __init__(
        self,
        repo: HouseRepository,
        session: AsyncSession,
        storage: ImageStorage,
    ):
        self.repo = repo
        self.session = session
        self.storage = storage

    def _extract_public_id_for_raw(self, url: str) -> str | None:
        """Extracts public_id for documents (with extension)."""
        if not url:
            return None
        match = re.search(r"/upload/(?:v\d+/)?(swipe_project/.*)", url)
        if match:
            return match.group(1)
        return None

    async def create_house(self, user: User, data: HouseCreate) -> HouseResponse:
        """Creates a new House Complex."""
        if user.role not in [UserRole.DEVELOPER, UserRole.MODERATOR]:
            logger.warning(
                "User %s denied creating house (role: %s)", user.id, user.role
            )
            raise PermissionDeniedError()

        logger.info("Creating new house structure: %s by user %s", data.name, user.id)
        house = await self.repo.create_house(data, owner_id=user.id)
        await self.session.commit()
        return house

    async def get_houses(self) -> Sequence[HouseResponse]:
        """Returns a list of all House Complexes."""
        return await self.repo.get_all_houses()

    async def update_house_info(
        self, user: User, house_id: int, data: HouseInfoUpdate
    ) -> HouseResponse:
        """Updates House Complex information."""
        house = await self.repo.get_house_by_id(house_id)
        if not house:
            raise ResourceNotFoundError()

        check_owner_or_admin(user, house.owner_id, "You cannot edit this house info")

        update_data = data.model_dump(exclude_unset=True)
        updated_house = await self.repo.update_house_info(house, update_data)
        await self.session.commit()

        return updated_house

    async def upload_main_image(
        self, user: User, house_id: int, file: UploadFile
    ) -> HouseResponse:
        """
        Uploads the main image for the House Complex.
        Deletes the old image if it exists.
        """
        if not file.content_type.startswith("image/"):
            logger.warning("Invalid file type uploaded for house main image")
            raise BadRequestError()

        house = await self.repo.get_house_by_id(house_id)
        if not house:
            raise ResourceNotFoundError()

        check_owner_or_admin(user, house.owner_id, "You cannot edit this house info")

        if house.info and house.info.main_image:
            old_public_id = extract_public_id_for_image(house.info.main_image)
            if old_public_id:
                await self.storage.delete_file(old_public_id, resource_type="image")

        image_url = await self.storage.upload_file(
            file.file, folder=f"houses/{house_id}/general"
        )

        updated_house = await self.repo.update_house_info(
            house, {"main_image": image_url}
        )
        await self.session.commit()

        logger.info("Updated main image for house %s", house_id)
        return updated_house

    async def add_news(
        self, user: User, house_id: int, data: NewsCreate
    ) -> NewsResponse:
        """Adds news to the House Complex."""
        house = await self.repo.get_house_by_id(house_id)
        if not house:
            raise ResourceNotFoundError()

        check_owner_or_admin(user, house.owner_id, "You cannot add news to this house")

        news = await self.repo.add_news(house_id, data)
        await self.session.commit()
        return news

    async def delete_news(self, user: User, news_id: int):
        """Deletes news from the House Complex."""
        news = await self.repo.get_news_by_id(news_id)
        if not news:
            raise ResourceNotFoundError()

        check_owner_or_admin(user, news.house.owner_id, "You cannot delete this news")

        await self.repo.delete_news(news_id)
        await self.session.commit()
        return {"status": "deleted", "id": news_id}

    async def add_document(
        self, user: User, house_id: int, file: UploadFile, is_excel: bool
    ) -> DocumentResponse:
        """Adds a document to the House Complex."""
        if file.size == 0:
            logger.warning("Empty file uploaded")
            raise BadRequestError()

        house = await self.repo.get_house_by_id(house_id)
        if not house:
            raise ResourceNotFoundError()

        check_owner_or_admin(
            user, house.owner_id, "You cannot add documents to this house"
        )

        file_obj = file.file
        if hasattr(file_obj, "name"):
            file_obj.name = file.filename

        doc_url = await self.storage.upload_file(
            file_obj, folder=f"houses/{house_id}/docs", filename=file.filename
        )

        doc_data = DocumentCreate(doc_url=doc_url, is_excel=is_excel)
        document = await self.repo.add_document(house_id, doc_data)
        await self.session.commit()
        return document

    async def delete_document(self, user: User, doc_id: int):
        """Deletes a document from the House Complex."""
        doc = await self.repo.get_document_by_id(doc_id)
        if not doc:
            raise ResourceNotFoundError()

        check_owner_or_admin(
            user, doc.house.owner_id, "You cannot delete this document"
        )

        public_id = self._extract_public_id_for_raw(doc.doc_url)
        if public_id:
            await self.storage.delete_file(public_id, resource_type="raw")

        await self.repo.delete_document(doc_id)
        await self.session.commit()
        return {"status": "deleted", "id": doc_id}
