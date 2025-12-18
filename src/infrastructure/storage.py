"""src/infrastructure/storage.py."""

from typing import BinaryIO
import cloudinary
import cloudinary.uploader
from fastapi.concurrency import run_in_threadpool

from src.config import settings


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
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            raise e

    async def delete_file(self, public_id: str):
        """Удаление файла"""
        await run_in_threadpool(cloudinary.uploader.destroy, public_id)
