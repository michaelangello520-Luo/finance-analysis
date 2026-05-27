import akshare as ak
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock
from app.models.financial_data import FinancialData


async def fetch_and_save_stock(db: AsyncSession, code: str) -> Stock | None:
    result = await db.execute(select(Stock).where(Stock.code == code))
    stock = result.scalars().first()

    try:
        df = ak.stock_individual_info_em(symbol=code)
        info = dict(zip(df["item"], df["value"]))
        name = info.get("股票简称", "")
    except Exception:
        name = code

    if not stock:
        stock = Stock(code=code, name=name)
        db.add(stock)
        await db.flush()
    else:
        stock.name = name

    return stock


async def fetch_and_save_financials(db: AsyncSession, stock: Stock) -> list[FinancialData]:
    try:
        df = ak.stock_financial_analysis_indicator(symbol=stock.code)
        if df is None or df.empty:
            return []
    except Exception:
        return []

    records = []
    for _, row in df.head(4).iterrows():
        period = str(row.get("日期", ""))[:10]
        if not period:
            continue

        result = await db.execute(
            select(FinancialData).where(
                FinancialData.stock_id == stock.id,
                FinancialData.period == period,
            )
        )
        existing = result.scalars().first()
        if existing:
            continue

        fd = FinancialData(
            stock_id=stock.id,
            period=period,
            roe=_safe_float(row.get("净资产收益率(%)")),
            gross_margin=_safe_float(row.get("销售毛利率(%)")),
            net_margin=_safe_float(row.get("销售净利率(%)")),
            eps=_safe_float(row.get("每股收益")),
            revenue=_safe_float(row.get("营业收入(元)")),
            net_profit=_safe_float(row.get("净利润(元)")),
        )
        db.add(fd)
        records.append(fd)

    await db.flush()
    return records


def _safe_float(val) -> float | None:
    if val is None or val == "-" or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
