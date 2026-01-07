"""src/apps/users/tests/test_profile.py."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers):
    """Profile text field update test."""
    payload = {"first_name": "UpdatedName", "last_name": "UpdatedSurname"}

    response = await client.patch("/users/me", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "UpdatedName"
    assert data["last_name"] == "UpdatedSurname"


@pytest.mark.asyncio
async def test_upload_avatar(client: AsyncClient, auth_headers):
    """Avatar upload test."""
    files = {"file": ("avatar.jpg", b"fake_image_content", "image/jpeg")}

    response = await client.post("/users/me/avatar", files=files, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()

    assert "cloudinary" in data["avatar"]
