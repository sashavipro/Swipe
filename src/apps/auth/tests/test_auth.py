"""src/apps/auth/tests/test_auth.py."""

import json
import pytest
from httpx import AsyncClient
from redis.asyncio import Redis
from dishka import AsyncContainer
from tests.factories.users import UserRegisterFactory


@pytest.mark.asyncio
async def test_register_user_flow(client: AsyncClient, app):
    """
    Tests the complete user registration flow:
    1. Initiate registration (send code).
    2. Verify code.
    3. Login.
    """
    user_data = UserRegisterFactory.build()

    # Step 1: Register
    response = await client.post("/auth/register", json=user_data.model_dump())
    assert response.status_code == 200
    assert response.json()["status"] == "pending_verification"

    # Step 2: Get code from Redis
    container: AsyncContainer = app.state.dishka_container
    redis: Redis = await container.get(Redis)

    redis_key = f"registration:{user_data.email}"
    raw_data = await redis.get(redis_key)
    assert raw_data is not None

    code = json.loads(raw_data)["code"]

    # Step 3: Verify
    verify_response = await client.post(
        "/auth/verify", json={"email": user_data.email, "code": code}
    )

    assert verify_response.status_code == 201
    assert verify_response.json()["email"] == user_data.email

    # Step 4: Login
    login_response = await client.post(
        "/auth/login", json={"email": user_data.email, "password": user_data.password}
    )

    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
