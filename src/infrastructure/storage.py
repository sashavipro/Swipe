"""src/infrastructure/storage.py."""

import logging
from typing import BinaryIO
import cloudinary
import cloudinary.uploader
from fastapi.concurrency import run_in_threadpool

from src.config import settings

logger = logging.getLogger(__name__)


class ImageStorage:
    """
    Сервис для работы с Cloudinary.
    Позволяет загружать и удалять изображения.
    """

    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )

    async def upload_file(self, file: BinaryIO, folder: str = "general") -> str:
        """
        Загружает файл в Cloudinary и возвращает Secure URL.
        Работает асинхронно через тредпул.
        """
        try:
            result = await run_in_threadpool(
                cloudinary.uploader.upload,
                file,
                folder=f"swipe_project/{folder}",
                resource_type="auto",
            )
            return result.get("secure_url")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error uploading to Cloudinary: %s", e, exc_info=True)
            raise

    async def delete_file(self, public_id: str):
        """Удаление файла"""
        try:
            await run_in_threadpool(cloudinary.uploader.destroy, public_id)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error deleting file %s from Cloudinary: %s",
                public_id,
                e,
                exc_info=True,
            )
