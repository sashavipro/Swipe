"""src/repositories/users.py."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import ResourceAlreadyExistsError
from src.models.users import User, UserRole, AgentContact, BlackList, Complaint
from src.schemas.users import UserCreateBase, AgentContactSchema, ComplaintCreate

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
            raise ResourceAlreadyExistsError(
                "User with this email or phone number already exists."
            ) from e

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
            raise ResourceAlreadyExistsError(
                "New email or phone number is already in use by another user."
            ) from e

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

    async def add_to_blacklist(self, admin_id: int, user_id: int):
        """Adds a user to the blacklist."""
        stmt = select(BlackList).where(BlackList.blocked_user_id == user_id)
        if (await self.session.execute(stmt)).scalar_one_or_none():
            return

        entry = BlackList(user_id=admin_id, blocked_user_id=user_id)
        self.session.add(entry)
        await self.session.flush()

    async def remove_from_blacklist(self, user_id: int):
        """Removes a user from the blacklist."""
        stmt = select(BlackList).where(BlackList.blocked_user_id == user_id)
        result = await self.session.execute(stmt)
        entry = result.scalar_one_or_none()

        if entry:
            await self.session.delete(entry)
            await self.session.flush()

    async def is_user_banned(self, user_id: int) -> bool:
        """Checks if a user is in the blacklist."""
        stmt = select(BlackList).where(BlackList.blocked_user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_users(self, role: UserRole | None = None) -> list[User]:
        """
        Returns a list of users.
        If a role is provided, filters by it.
        """
        stmt = select(User).order_by(User.id)

        if role:
            stmt = stmt.where(User.role == role)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_user(self, user: User) -> None:
        """Deletes a user."""
        await self.session.delete(user)
        await self.session.flush()

    async def create_complaint(
        self, reporter_id: int, data: ComplaintCreate
    ) -> Complaint:
        """Creates a new complaint against a user."""
        complaint = Complaint(
            reporter_id=reporter_id,
            reported_user_id=data.reported_user_id,
            reason=data.reason,
            description=data.description,
        )
        self.session.add(complaint)
        await self.session.flush()
        return complaint

    async def list_complaints(self, resolved: bool = False) -> list[Complaint]:
        """List complaints (default: active/unresolved only)."""
        stmt = (
            select(Complaint)
            .where(Complaint.is_resolved == resolved)
            .order_by(Complaint.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def resolve_complaint(self, complaint_id: int):
        """Mark a complaint as resolved."""
        stmt = select(Complaint).where(Complaint.id == complaint_id)
        result = await self.session.execute(stmt)
        complaint = result.scalar_one_or_none()
        if complaint:
            complaint.is_resolved = True
            await self.session.flush()
