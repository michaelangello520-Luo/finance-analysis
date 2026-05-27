import pytest
from sqlalchemy import select

from app.models.stock import Stock
from app.models.industry import Industry


@pytest.mark.asyncio
async def test_create_stock(db_session):
    stock = Stock(code="000001", name="平安银行")
    db_session.add(stock)
    await db_session.commit()
    await db_session.refresh(stock)
    assert stock.id is not None
    assert stock.code == "000001"
    assert stock.name == "平安银行"


@pytest.mark.asyncio
async def test_create_industry(db_session):
    industry = Industry(name="机器人", sector="高端装备")
    db_session.add(industry)
    await db_session.commit()
    await db_session.refresh(industry)
    assert industry.id is not None
    assert industry.name == "机器人"


@pytest.mark.asyncio
async def test_stock_industry_relation(db_session):
    industry = Industry(name="机器人", sector="高端装备")
    db_session.add(industry)
    await db_session.flush()

    stock = Stock(code="002747", name="埃斯顿", industry_id=industry.id)
    db_session.add(stock)
    await db_session.commit()
    await db_session.refresh(stock)
    assert stock.industry_id == industry.id
