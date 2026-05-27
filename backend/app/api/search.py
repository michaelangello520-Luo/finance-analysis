from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stock import Stock
from app.models.industry import Industry
from app.schemas.search import SearchResult
from app.schemas.stock import StockListItem
from app.schemas.industry import IndustryListItem

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResult)
async def search(q: str = Query(default="", max_length=50), db: AsyncSession = Depends(get_db)):
    if not q.strip():
        return SearchResult()

    like_pattern = f"%{q}%"

    stock_stmt = select(Stock).where(
        or_(Stock.name.like(like_pattern), Stock.code.like(like_pattern))
    ).limit(10)
    stock_result = await db.execute(stock_stmt)
    stocks = [StockListItem.model_validate(s) for s in stock_result.scalars().all()]

    industry_stmt = select(Industry).where(Industry.name.like(like_pattern)).limit(10)
    industry_result = await db.execute(industry_stmt)
    industries = [IndustryListItem.model_validate(i) for i in industry_result.scalars().all()]

    return SearchResult(stocks=stocks, industries=industries)
