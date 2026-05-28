import asyncio

import akshare as ak
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


@router.get("/hot-industries")
async def get_hot_industries(limit: int = Query(default=8, ge=1, le=20)):
    """Fetch hot industries from THS board ranking (sorted by change %)."""
    try:
        df = await asyncio.to_thread(ak.stock_board_industry_summary_ths)
        if df is None or df.empty:
            return {"industries": []}

        # Columns: 序号, 名称, 涨跌幅, 总成交额, 领涨股, 涨跌数...
        top = df.head(limit)
        result = []
        for _, row in top.iterrows():
            name = str(row.iloc[1])  # 名称
            change = float(row.iloc[2]) if row.iloc[2] else 0  # 涨跌幅
            lead_stock = str(row.iloc[9]) if len(row) > 9 else ""  # 领涨股名称
            result.append({"name": name, "change": round(change, 2), "lead_stock": lead_stock})
        return {"industries": result}
    except Exception as e:
        raise HTTPException(500, f"获取热门行业失败: {str(e)}")


@router.get("/hot-stocks")
async def get_hot_stocks(limit: int = Query(default=10, ge=1, le=20)):
    """Fetch hot stocks from THS ranking (top gaining stocks)."""
    try:
        df = await asyncio.to_thread(ak.stock_changes_em)
        if df is None or df.empty:
            return {"stocks": []}

        # Columns: 序号, 代码, 名称, 最新价, 涨跌幅, 涨跌额, 成交量, 成交额, 振幅, 换手率...
        top = df.head(limit)
        result = []
        for _, row in top.iterrows():
            code = str(row.iloc[1])
            name = str(row.iloc[2])
            price = float(row.iloc[3]) if row.iloc[3] else 0
            change = float(row.iloc[4]) if row.iloc[4] else 0
            result.append({"code": code, "name": name, "price": round(price, 2), "change": round(change, 2)})
        return {"stocks": result}
    except Exception:
        # Fallback to THS 连续上涨
        try:
            df = await asyncio.to_thread(ak.stock_rank_lxsz_ths)
            if df is None or df.empty:
                return {"stocks": []}
            top = df.head(limit)
            result = []
            for _, row in top.iterrows():
                code = str(row.iloc[1])
                name = str(row.iloc[2])
                price = float(row.iloc[4]) if row.iloc[4] else 0
                change = float(row.iloc[7]) if row.iloc[7] else 0
                days = int(row.iloc[6]) if row.iloc[6] else 0
                result.append({"code": code, "name": name, "price": round(price, 2), "change": round(change, 2), "days_up": days})
            return {"stocks": result}
        except Exception as e:
            raise HTTPException(500, f"获取热门股票失败: {str(e)}")
