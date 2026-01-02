"""src/tests/fixtures/auth.py."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users import UserRepository
from src.infrastructure.security.jwt import JWTHandler
from src.infrastructure.security.password import PasswordHandler
from src.models.users import UserRole
from src.tests.factories.users import UserCreateFactory


async def _create_user_and_token(container, role: UserRole) -> dict:
    """
    Support function for creating a user and token.
    """
    user_data = UserCreateFactory.build()

    async with container() as request_container:
        user_repo = await request_container.get(UserRepository)
        session = await request_container.get(AsyncSession)

        user = await user_repo.create_user(
            data=user_data,
            hashed_password=PasswordHandler.get_password_hash("pass"),
            role=role,
        )
        await session.commit()

        token = JWTHandler.create_access_token(
            {"sub": str(user.id), "role": user.role.value}
        )
        return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers(app):
    """
    Creates a regular user (USER) and returns authorization headers.
    """
    return await _create_user_and_token(app.state.dishka_container, UserRole.USER)


@pytest_asyncio.fixture
async def developer_headers(app):
    """
    Creates a developer (DEVELOPER) and returns headers.
    """
    return await _create_user_and_token(app.state.dishka_container, UserRole.DEVELOPER)


@pytest_asyncio.fixture
async def moderator_headers(app):
    """
    Creates a moderator (MODERATOR) and returns the headers.
    """
    return await _create_user_and_token(app.state.dishka_container, UserRole.MODERATOR)
