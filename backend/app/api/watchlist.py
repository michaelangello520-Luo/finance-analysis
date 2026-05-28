from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.watchlist import Watchlist
from app.models.stock import Stock
from app.models.industry import Industry

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


class WatchlistAdd(BaseModel):
    target_type: str  # "stock" or "industry"
    target_id: int


@router.get("")
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Watchlist).order_by(Watchlist.created_at.desc()))
    items = result.scalars().all()

    out = []
    for item in items:
        name = ""
        code = None
        if item.target_type == "stock":
            sr = await db.execute(select(Stock).where(Stock.id == item.target_id))
            stock = sr.scalar_one_or_none()
            if stock:
                name, code = stock.name, stock.code
        elif item.target_type == "industry":
            ir = await db.execute(select(Industry).where(Industry.id == item.target_id))
            ind = ir.scalar_one_or_none()
            if ind:
                name = ind.name
        out.append({
            "id": item.id,
            "target_type": item.target_type,
            "target_id": item.target_id,
            "name": name,
            "code": code,
        })
    return out


@router.post("")
async def add_to_watchlist(body: WatchlistAdd, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Watchlist).where(
            Watchlist.target_type == body.target_type,
            Watchlist.target_id == body.target_id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(400, "已在关注列表中")

    wl = Watchlist(target_type=body.target_type, target_id=body.target_id)
    db.add(wl)
    await db.commit()
    return {"id": wl.id, "message": "已添加到关注列表"}


@router.delete("/{item_id}")
async def remove_from_watchlist(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Watchlist).where(Watchlist.id == item_id))
    wl = result.scalar_one_or_none()
    if not wl:
        raise HTTPException(404, "关注记录不存在")
    await db.delete(wl)
    await db.commit()
    return {"message": "已从关注列表移除"}


@router.get("/check")
async def check_watchlist(
    target_type: str, target_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.target_type == target_type,
            Watchlist.target_id == target_id,
        )
    )
    item = result.scalars().first()
    return {"watched": item is not None, "id": item.id if item else None}
