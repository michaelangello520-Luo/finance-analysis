from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.stock import Stock
from app.models.industry import Industry
from app.schemas.stock import StockDetail, StockListItem
from app.schemas.industry import IndustryDetail, IndustryListItem
from app.schemas.search import SearchResult
from app.services.stock_data import fetch_and_save_stock, fetch_and_save_financials
from app.services.industry_data import fetch_and_save_industry, fetch_industry_stocks
from app.services.research_report import fetch_and_save_reports

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/stock")
async def collect_stock_data(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    stock = await fetch_and_save_stock(db, code)
    if not stock:
        raise HTTPException(400, f"无法获取股票 {code} 的数据")
    financials = await fetch_and_save_financials(db, stock)
    await db.commit()
    return {"message": f"已采集 {stock.name}({stock.code}) 数据，{len(financials)} 条财务记录"}


@router.post("/industry")
async def collect_industry_data(
    name: str = Query(...), sector: str = Query(default=""), db: AsyncSession = Depends(get_db)
):
    industry = await fetch_and_save_industry(db, name, sector)
    if not industry:
        raise HTTPException(400, f"无法创建行业 {name}")
    stocks = await fetch_industry_stocks(db, industry)
    reports = await fetch_and_save_reports(db, name, target_type="industry", industry_id=industry.id)
    await db.commit()
    return {
        "message": f"已采集行业 {name} 数据，{len(stocks)} 只成分股，{len(reports)} 份研报",
        "id": industry.id,
    }


@router.post("/report")
async def collect_reports(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    reports = await fetch_and_save_reports(db, q)
    await db.commit()
    return {"message": f"已采集 {len(reports)} 份研报"}
