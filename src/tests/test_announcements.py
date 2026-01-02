"""src/tests/test_announcements.py."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.tests.factories.announcement import AnnouncementCreateFactory
from src.tests.utils import approve_announcement


@pytest.mark.asyncio
async def test_create_announcement(client: AsyncClient, auth_headers):
    """Ad creation test."""
    announcement_data = AnnouncementCreateFactory.build()
    payload = announcement_data.model_dump(mode="json")

    response = await client.post(
        "/real-estate/announcements", json=payload, headers=auth_headers
    )

    assert response.status_code == 201, f"Error: {response.text}"
    data = response.json()
    assert data["address"] == announcement_data.address
    assert data["user_id"] is not None


@pytest.mark.asyncio
async def test_get_announcements_list(client: AsyncClient, app, auth_headers):
    """Test to obtain a list of ads."""
    data = AnnouncementCreateFactory.build()
    payload = data.model_dump(mode="json")
    create_resp = await client.post(
        "/real-estate/announcements", json=payload, headers=auth_headers
    )
    assert create_resp.status_code == 201

    announcement_id = create_resp.json()["id"]

    container = app.state.dishka_container
    async with container() as request_container:
        session = await request_container.get(AsyncSession)
        await approve_announcement(session, announcement_id)

    response = await client.get("/real-estate/announcements?limit=10&offset=0")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
