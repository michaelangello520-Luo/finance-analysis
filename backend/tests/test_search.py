import pytest

from app.models.stock import Stock
from app.models.industry import Industry


@pytest.mark.asyncio
async def test_search_returns_matching_stocks(client, db_session):
    db_session.add(Stock(code="000001", name="平安银行"))
    db_session.add(Stock(code="600036", name="招商银行"))
    await db_session.commit()

    response = await client.get("/api/search?q=银行")
    assert response.status_code == 200
    data = response.json()
    assert len(data["stocks"]) == 2
    assert data["stocks"][0]["code"] == "000001"


@pytest.mark.asyncio
async def test_search_returns_matching_industries(client, db_session):
    db_session.add(Industry(name="机器人", sector="高端装备"))
    db_session.add(Industry(name="新能源", sector="电力设备"))
    await db_session.commit()

    response = await client.get("/api/search?q=机器")
    assert response.status_code == 200
    data = response.json()
    assert len(data["industries"]) == 1
    assert data["industries"][0]["name"] == "机器人"


@pytest.mark.asyncio
async def test_search_empty_query_returns_empty(client):
    response = await client.get("/api/search?q=")
    assert response.status_code == 200
    data = response.json()
    assert data["stocks"] == []
    assert data["industries"] == []


@pytest.mark.asyncio
async def test_search_stock_by_code(client, db_session):
    db_session.add(Stock(code="000001", name="平安银行"))
    await db_session.commit()

    response = await client.get("/api/search?q=000001")
    assert response.status_code == 200
    data = response.json()
    assert len(data["stocks"]) == 1
    assert data["stocks"][0]["code"] == "000001"
