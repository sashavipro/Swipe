"""src/apps/users/repositories/user_profile.py."""

import logging
from typing import Any
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.auth.schemas import UserCreateBase
from src.apps.users.models import User, UserRole, AgentContact, BlackList
from src.apps.users.schemas.user_profile import AgentContactSchema
from src.core.exceptions import ResourceAlreadyExistsError

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository for working with users.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_one(self, **filters: Any) -> User | None:
        """
        Internal universal method for getting one user by filters.
        Uses SQLAlchemy filter_by (e.g., id=1, email="test@test.com").
        """
        stmt = select(User).filter_by(**filters)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.debug("User not found by filters: %s", filters)
        else:
            logger.debug("User found by filters: %s", filters)

        return user

    async def get_by_email(self, email: str) -> User | None:
        """Searches for a user by email."""
        return await self._get_one(email=email)

    async def get_by_id(self, user_id: int) -> User | None:
        """Searches for a user by ID."""
        return await self._get_one(id=user_id)

    async def create_user(
        self, data: UserCreateBase, hashed_password: str, role: UserRole = UserRole.USER
    ) -> User:
        """Creates a new user in the database."""
        logger.info("Attempting to create user: email=%s, role=%s", data.email, role)

        try:
            user = User(
                email=data.email,
                hashed_password=hashed_password,
                first_name=data.first_name,
                last_name=data.last_name,
                phone=data.phone,
                role=role,
            )
            self.session.add(user)
            await self.session.flush()

            await self.session.refresh(user, attribute_names=["agent_contact"])

            logger.info("User created successfully: id=%s", user.id)
            return user

        except IntegrityError as e:
            logger.warning(
                "Failed to create user: Integrity error (likely duplicate). Error: %s",
                e,
            )
            await self.session.rollback()
            raise ResourceAlreadyExistsError() from e

    async def update_user(self, user: User, update_data: dict) -> User:
        """Updates user fields."""
        logger.info(
            "Updating user_id=%s. Fields: %s", user.id, list(update_data.keys())
        )

        try:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user, attribute_names=["agent_contact"])
            return user

        except IntegrityError as e:
            logger.warning("Failed to update user %s: Duplicate data.", user.id)
            await self.session.rollback()
            raise ResourceAlreadyExistsError() from e

    async def update_agent_contact(self, user: User, data: AgentContactSchema):
        """
        Creates or updates agent contacts for the user.
        """
        logger.info("Updating agent contact for user_id=%s", user.id)

        if user.agent_contact:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user.agent_contact, key, value)
        else:
            new_contact = AgentContact(
                user_id=user.id, **data.model_dump(exclude_unset=True)
            )
            self.session.add(new_contact)
            user.agent_contact = new_contact

        await self.session.flush()

    async def is_user_banned(self, user_id: int) -> bool:
        """Checks if a user is in the blacklist."""
        stmt = select(BlackList).where(BlackList.blocked_user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
