from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.stock_data import fetch_and_save_stock, fetch_and_save_financials, extract_name_from_reports
from app.services.industry_data import fetch_and_save_industry, fetch_industry_stocks
from app.services.research_report import fetch_and_save_reports

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/stock")
async def collect_stock_data(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    stock = await fetch_and_save_stock(db, code)
    if not stock:
        raise HTTPException(400, f"无法获取股票 {code} 的数据")

    financials = await fetch_and_save_financials(db, stock)

    # Collect reports - use name if available, otherwise code
    query = stock.name if stock.name != stock.code else stock.code
    reports = await fetch_and_save_reports(db, query, target_type="stock", stock_id=stock.id)

    # If name is still code, try extracting from report titles
    if stock.name == stock.code and reports:
        name = extract_name_from_reports(reports)
        if name:
            stock.name = name

    await db.commit()
    return {
        "message": f"已采集 {stock.name}({stock.code})，{len(financials)} 条财务数据，{len(reports)} 份研报",
        "id": stock.id,
    }


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
        "message": f"已采集行业 {name}，{len(stocks)} 只成分股，{len(reports)} 份研报",
        "id": industry.id,
    }


@router.post("/report")
async def collect_reports(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    reports = await fetch_and_save_reports(db, q)
    await db.commit()
    return {"message": f"已采集 {len(reports)} 份研报"}
