from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.stock import Stock
from app.schemas.stock import StockDetail

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/{code}", response_model=StockDetail)
async def get_stock_detail(code: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Stock).where(Stock.code == code).options(
        selectinload(Stock.financial_data),
        selectinload(Stock.reports),
    )
    result = await db.execute(stmt)
    stock = result.scalars().first()
    if not stock:
        raise HTTPException(404, f"股票 {code} 不存在，请先通过 POST /api/data/stock?code={code} 采集数据")
    return stock
