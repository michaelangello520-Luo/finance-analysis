import akshare as ak
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock
from app.models.industry import Industry, StockIndustry


async def fetch_and_save_industry(db: AsyncSession, name: str, sector: str = "") -> Industry | None:
    result = await db.execute(select(Industry).where(Industry.name == name))
    industry = result.scalars().first()

    if not industry:
        industry = Industry(name=name, sector=sector)
        db.add(industry)
        await db.flush()

    return industry


async def fetch_industry_stocks(db: AsyncSession, industry: Industry) -> list[Stock]:
    """Fetch constituent stocks for an industry/board from AKShare."""
    stocks = []

    # Try concept boards first, then industry boards
    board_code = None
    cons_df = None

    for board_type in ["concept", "industry"]:
        try:
            if board_type == "concept":
                df = ak.stock_board_concept_name_em()
            else:
                df = ak.stock_board_industry_name_em()

            matched = df[df["板块名称"].str.contains(industry.name, na=False)]
            if matched.empty:
                continue

            board_code = str(matched.iloc[0]["板块代码"])

            if board_type == "concept":
                cons_df = ak.stock_board_concept_cons_em(symbol=board_code)
            else:
                cons_df = ak.stock_board_industry_cons_em(symbol=board_code)

            if cons_df is not None and not cons_df.empty:
                break
        except Exception:
            continue

    if cons_df is None or cons_df.empty:
        return stocks

    for _, row in cons_df.head(20).iterrows():
        code = str(row.get("代码", ""))
        sname = str(row.get("名称", ""))
        if not code:
            continue

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
