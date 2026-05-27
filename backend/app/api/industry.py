from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.industry import Industry
from app.schemas.industry import IndustryDetail

router = APIRouter(prefix="/api/industries", tags=["industries"])


@router.get("/{industry_id}", response_model=IndustryDetail)
async def get_industry_detail(industry_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Industry).where(Industry.id == industry_id).options(
        selectinload(Industry.stocks),
        selectinload(Industry.reports),
    )
    result = await db.execute(stmt)
    industry = result.scalars().first()
    if not industry:
        raise HTTPException(404, f"行业 {industry_id} 不存在，请先通过 POST /api/data/industry?name=xxx 采集数据")
    return industry
