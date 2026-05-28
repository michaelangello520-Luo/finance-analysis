import re

import akshare as ak
import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock
from app.models.industry import Industry, StockIndustry

THS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://q.10jqka.com.cn/",
}


async def fetch_and_save_industry(db: AsyncSession, name: str, sector: str = "") -> Industry | None:
    result = await db.execute(select(Industry).where(Industry.name == name))
    industry = result.scalars().first()

    if not industry:
        industry = Industry(name=name, sector=sector)
        db.add(industry)
        await db.flush()

    return industry


def _find_ths_board_code(name: str, board_type: str = "concept") -> str | None:
    """Find THS board code by name. board_type: 'concept' or 'industry'."""
    try:
        if board_type == "concept":
            df = ak.stock_board_concept_name_ths()
        else:
            df = ak.stock_board_industry_name_ths()
        matched = df[df["name"].str.contains(name, na=False)]
        if matched.empty:
            return None
        return str(matched.iloc[0]["code"])
    except Exception:
        return None


def _fetch_ths_board_stocks(board_code: str, board_type: str = "concept") -> list[dict]:
    """Scrape constituent stocks from THS board page."""
    try:
        if board_type == "concept":
            url = f"http://q.10jqka.com.cn/gn/detail/field/264648/order/desc/page/1/ajax/1/code/{board_code}"
        else:
            url = f"http://q.10jqka.com.cn/thshy/detail/field/264648/order/desc/page/1/ajax/1/code/{board_code}"

        r = requests.get(url, headers=THS_HEADERS, timeout=15)
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        stocks = []
        for row in soup.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) >= 3:
                code = tds[1].get_text(strip=True)
                sname = tds[2].get_text(strip=True)
                if re.match(r"^\d{6}$", code):
                    stocks.append({"code": code, "name": sname})
        return stocks
    except Exception:
        return []


async def fetch_industry_stocks(db: AsyncSession, industry: Industry) -> list[Stock]:
    """Fetch constituent stocks using THS data source."""
    stocks = []
    name = industry.name

    # Try concept board first, then industry board
    for board_type in ["concept", "industry"]:
        board_code = _find_ths_board_code(name, board_type)
        if not board_code:
            continue

        stock_list = _fetch_ths_board_stocks(board_code, board_type)
        if stock_list:
            break
    else:
        return stocks

    for item in stock_list[:20]:
        code = item["code"]
        sname = item["name"]

        result = await db.execute(select(Stock).where(Stock.code == code))
        stock = result.scalars().first()
        if not stock:
            stock = Stock(code=code, name=sname, industry_id=industry.id)
            db.add(stock)
            await db.flush()
        elif not stock.industry_id:
            stock.industry_id = industry.id

        link_result = await db.execute(
            select(StockIndustry).where(
                StockIndustry.stock_id == stock.id,
                StockIndustry.industry_id == industry.id,
            )
        )
        if not link_result.scalars().first():
            db.add(StockIndustry(stock_id=stock.id, industry_id=industry.id))

        stocks.append(stock)

    await db.flush()
    return stocks
