"""src/tests/test_favorites.py."""

import pytest
from httpx import AsyncClient

from src.tests.factories.announcement import AnnouncementCreateFactory


@pytest.mark.asyncio
async def test_favorites_lifecycle(client: AsyncClient, auth_headers):
    """
    Checks the entire cycle: Add -> Get list -> Delete.
    """
    announcement_data = AnnouncementCreateFactory.build()
    create_resp = await client.post(
        "/real-estate/announcements",
        json=announcement_data.model_dump(mode="json"),
        headers=auth_headers,
    )
    announcement_id = create_resp.json()["id"]

    resp_add = await client.post(
        f"/users/me/favorites/{announcement_id}", headers=auth_headers
    )
    assert resp_add.status_code == 201
    assert resp_add.json()["status"] == "added"

    resp_list = await client.get("/users/me/favorites", headers=auth_headers)
    assert resp_list.status_code == 200
    favorites = resp_list.json()
    assert len(favorites) == 1
    assert favorites[0]["id"] == announcement_id

    resp_del = await client.delete(
        f"/users/me/favorites/{announcement_id}", headers=auth_headers
    )
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "removed"

    resp_list_empty = await client.get("/users/me/favorites", headers=auth_headers)
    assert len(resp_list_empty.json()) == 0
