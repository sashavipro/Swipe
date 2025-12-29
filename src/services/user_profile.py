"""src/services/user_profile.py."""

import logging

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    BadRequestError,
)
from src.repositories.users import UserRepository
from src.infrastructure.storage import ImageStorage
from src.infrastructure.security.password import PasswordHandler
from src.schemas.users import UserUpdate, EmployeeCreate, UserResponse

logger = logging.getLogger(__name__)


class UserProfileService:
    """
    Service for working with users.
    """

    def __init__(
        self, repo: UserRepository, session: AsyncSession, storage: ImageStorage
    ):
        self.repo = repo
        self.session = session
        self.storage = storage

    async def create_employee(self, data: EmployeeCreate) -> UserResponse:
        """
        Creates a user with a specified role.
        """
        logger.info("Creating employee with email: %s, role: %s", data.email, data.role)

        if await self.repo.get_by_email(data.email):
            logger.warning(
                "Employee creation failed: Email %s already exists", data.email
            )
            raise ResourceAlreadyExistsError()

        hashed_password = PasswordHandler.get_password_hash(data.password)

        user = await self.repo.create_user(data, hashed_password, role=data.role)
        await self.session.commit()

        logger.info("Employee created successfully: id=%s", user.id)
        return user

    async def update_my_profile(self, user_id: int, data: UserUpdate) -> UserResponse:
        """
        Updates user profile: personal data, settings, and agent contacts.
        """
        logger.info("Updating profile for user_id=%s", user_id)

        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError()

        user_data = data.model_dump(exclude_unset=True)
        agent_data = user_data.pop("agent_contact", None)

        if "email" in user_data:
            existing = await self.repo.get_by_email(user_data["email"])
            if existing and existing.id != user_id:
                logger.warning(
                    "Update failed: Email %s is taken by another user",
                    user_data["email"],
                )
                raise ResourceAlreadyExistsError()

        if user_data:
            await self.repo.update_user(user, user_data)

        if agent_data is not None:
            await self.repo.update_agent_contact(user, data.agent_contact)

        await self.session.commit()
        await self.session.refresh(user)

        logger.info("Profile updated successfully for user %s", user.id)
        return user

    async def update_avatar(self, user_id: int, file: UploadFile) -> UserResponse:
        """Upload and update avatar."""
        logger.info("Updating avatar for user_id=%s", user_id)

        if not file.content_type.startswith("image/"):
            logger.warning("Invalid file type uploaded for avatar")
            raise BadRequestError()

        user = await self.repo.get_by_id(user_id)
        if not user:
            logger.warning("Update avatar failed: User %s not found", user_id)
            raise ResourceNotFoundError()

        image_url = await self.storage.upload_file(file.file, folder="avatars")
        updated_user = await self.repo.update_user(user, {"avatar": image_url})

        await self.session.commit()
        logger.info("Avatar updated successfully for user %s", user.id)
        return updated_user
