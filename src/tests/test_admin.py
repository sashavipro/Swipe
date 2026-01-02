"""src/tests/test_admin.py."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users import UserRepository
from src.infrastructure.security.jwt import JWTHandler
from src.infrastructure.security.password import PasswordHandler
from src.tests.factories.users import UserCreateFactory


@pytest.mark.asyncio
async def test_ban_user(client: AsyncClient, moderator_headers, app):
    """Moderator bans user."""

    container = app.state.dishka_container
    victim_data = UserCreateFactory.build()

    async with container() as request_container:
        user_repo = await request_container.get(UserRepository)
        session = await request_container.get(AsyncSession)
        victim = await user_repo.create_user(
            victim_data, PasswordHandler.get_password_hash("pass")
        )
        await session.commit()
        victim_id = victim.id

    response = await client.post(
        f"/admin/users/{victim_id}/ban", headers=moderator_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "banned"

    victim_token = JWTHandler.create_access_token(
        {"sub": str(victim_id), "role": "user"}
    )
    victim_headers = {"Authorization": f"Bearer {victim_token}"}

    resp_check = await client.get("/users/me", headers=victim_headers)
    assert resp_check.status_code == 403
