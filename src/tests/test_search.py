"""src/tests/test_search.py."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.tests.factories.announcement import AnnouncementCreateFactory
from src.tests.utils import approve_announcement


@pytest.mark.asyncio
async def test_search_announcements_by_price(client: AsyncClient, app, auth_headers):
    """Price filter test."""
    container = app.state.dishka_container

    expensive = AnnouncementCreateFactory.build(price=10_000_000)
    resp1 = await client.post(
        "/real-estate/announcements",
        json=expensive.model_dump(mode="json"),
        headers=auth_headers,
    )
    id1 = resp1.json()["id"]

    cheap = AnnouncementCreateFactory.build(price=5_000_000)
    resp2 = await client.post(
        "/real-estate/announcements",
        json=cheap.model_dump(mode="json"),
        headers=auth_headers,
    )
    id2 = resp2.json()["id"]

    async with container() as request_container:
        session = await request_container.get(AsyncSession)
        await approve_announcement(session, id1)
        await approve_announcement(session, id2)

    response = await client.get("/real-estate/announcements/search?price_to=6000000")
    assert response.status_code == 200
    results = response.json()
    prices = [float(item["price"]) for item in results]
    assert 5_000_000.0 in prices
    assert 10_000_000.0 not in prices

    response_exp = await client.get(
        "/real-estate/announcements/search?price_from=9000000"
    )
    assert response_exp.status_code == 200
    results_exp = response_exp.json()
    prices_exp = [float(item["price"]) for item in results_exp]
    assert 10_000_000.0 in prices_exp
    assert 5_000_000.0 not in prices_exp
