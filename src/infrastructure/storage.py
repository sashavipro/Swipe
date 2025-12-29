"""src/infrastructure/storage.py."""

import logging
from typing import BinaryIO, Optional
import cloudinary
import cloudinary.uploader
from fastapi.concurrency import run_in_threadpool

from src.config import settings

logger = logging.getLogger(__name__)


class ImageStorage:
    """
    Service for working with Cloudinary.
    """

    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )

    async def upload_file(
        self,
        file_obj: BinaryIO,
        folder: str = "general",
        filename: Optional[str] = None,
    ) -> str:
        """Uploads file to Cloudinary."""
        try:
            upload_options = {
                "folder": f"swipe_project/{folder}",
                "resource_type": "auto",
            }

            if filename:
                upload_options["use_filename"] = True
                upload_options["unique_filename"] = True
                upload_options["public_id"] = filename

            result = await run_in_threadpool(
                cloudinary.uploader.upload,
                file_obj,
                **upload_options,
            )
            return result.get("secure_url")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error uploading to Cloudinary: %s", e, exc_info=True)
            raise

    async def delete_file(self, public_id: str, resource_type: str = "image"):
        """
        Deletes a file.
        IMPORTANT: for documents (pdf, xlsx) pass resource_type="raw".
        """
        try:
            logger.info(
                "Deleting from Cloudinary: id=%s, type=%s", public_id, resource_type
            )
            await run_in_threadpool(
                cloudinary.uploader.destroy,
                public_id,
                resource_type=resource_type,
                invalidate=True,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error deleting file %s (%s) from Cloudinary: %s",
                public_id,
                resource_type,
                e,
                exc_info=True,
            )
