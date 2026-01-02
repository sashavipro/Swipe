"""src/tests/test_houses.py."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_house_structure(client: AsyncClient, developer_headers):
    """
    Test for creating a complex LCD structure (requires DEVELOPER rights).
    """
    payload = {
        "name": "Grand Tower",
        "sections": [
            {
                "name": "Section A",
                "floors": [
                    {"number": 1, "apartments": [{"number": 101}, {"number": 102}]}
                ],
            }
        ],
        "info": {"address": "Baker Street 221B", "house_class": "business"},
    }

    response = await client.post(
        "/real-estate/houses", json=payload, headers=developer_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Grand Tower"
    assert len(data["sections"]) == 1


@pytest.mark.asyncio
async def test_user_cannot_create_house(client: AsyncClient, auth_headers):
    """A regular user cannot create an LCD."""
    payload = {"name": "Hacker House", "sections": []}
    response = await client.post(
        "/real-estate/houses", json=payload, headers=auth_headers
    )
    assert response.status_code == 403
