"""src/apps/announcement/tests/test_search.py."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.factories.announcement import AnnouncementCreateFactory
from tests.utils import approve_announcement


async def _create_and_approve(client, auth_headers, container, price):
    """Helper to create and approve an announcement."""
    data = AnnouncementCreateFactory.build(price=price)
    resp = await client.post(
        "/announcements/",
        json=data.model_dump(mode="json"),
        headers=auth_headers,
    )
    ann_id = resp.json()["id"]

    async with container() as request_container:
        session = await request_container.get(AsyncSession)
        await approve_announcement(session, ann_id)


@pytest.mark.asyncio
async def test_search_announcements_by_price(client: AsyncClient, app, auth_headers):
    """Price filter test."""
    container = app.state.dishka_container

    # Create test data
    await _create_and_approve(client, auth_headers, container, 10_000_000)
    await _create_and_approve(client, auth_headers, container, 5_000_000)

    # Test "price_to"
    response = await client.get("/announcements/search?price_to=6000000")
    assert response.status_code == 200
    results = response.json()
    prices = [float(item["price"]) for item in results]
    assert 5_000_000.0 in prices
    assert 10_000_000.0 not in prices

    # Test "price_from"
    response_exp = await client.get("/announcements/search?price_from=9000000")
    assert response_exp.status_code == 200
    results_exp = response_exp.json()
    prices_exp = [float(item["price"]) for item in results_exp]
    assert 10_000_000.0 in prices_exp
    assert 5_000_000.0 not in prices_exp
