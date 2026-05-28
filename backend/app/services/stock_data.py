import re
import akshare as ak
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock
from app.models.financial_data import FinancialData


async def fetch_and_save_stock(db: AsyncSession, code: str) -> Stock | None:
    result = await db.execute(select(Stock).where(Stock.code == code))
    stock = result.scalars().first()

    name = _get_stock_name(code)

    if not stock:
        stock = Stock(code=code, name=name)
        db.add(stock)
        await db.flush()
    else:
        if name != code:
            stock.name = name

    return stock


def _get_stock_name(code: str) -> str:
    """Try multiple AKShare APIs to get stock name."""
    # Method 1: stock_individual_info_em
    try:
        df = ak.stock_individual_info_em(symbol=code)
        info = dict(zip(df["item"], df["value"]))
        name = info.get("股票简称", "")
        if name:
            return name
    except Exception:
        pass

    # Method 2: stock_zh_a_spot_em (filter from all stocks)
    try:
        df = ak.stock_zh_a_spot_em()
        row = df[df["代码"] == code]
        if not row.empty:
            return str(row.iloc[0]["名称"])
    except Exception:
        pass

    return code


def extract_name_from_reports(reports: list) -> str | None:
    """Extract stock name from report titles."""
    for r in reports:
        title = ""
        if isinstance(r, dict):
            title = r.get("title", "")
        elif hasattr(r, "title"):
            title = r.title or ""
        if not title:
            continue
        # Pattern 1: "贵州茅台：累计回购" -> "贵州茅台"
        m = re.match(r"^([\u4e00-\u9fff]{2,8})[：:]", title)
        if m:
            return m.group(1)
        # Pattern 2: "XX股份/集团/科技" anywhere in title
        m = re.search(r"([\u4e00-\u9fff]{2,6})(?:股份|集团|科技|光电|医药|银行|证券|保险|能源|汽车|电子)", title)
        if m:
            return m.group(1)
        # Pattern 3: "关于XX" anywhere
        m = re.search(r"关于([\u4e00-\u9fff]{2,6})", title)
        if m:
            return m.group(1)
    return None


async def fetch_and_save_financials(db: AsyncSession, stock: Stock) -> list[FinancialData]:
    records = []

    # Primary: stock_financial_abstract_ths
    try:
        df = ak.stock_financial_abstract_ths(symbol=stock.code, indicator="按报告期")
        if df is not None and not df.empty:
            records = await _parse_ths_financials(db, stock, df)
    except Exception:
        pass

    if records:
        await db.flush()
        return records

    # Fallback: stock_financial_analysis_indicator
    try:
        df = ak.stock_financial_analysis_indicator(symbol=stock.code)
        if df is not None and not df.empty:
            records = await _parse_indicator_financials(db, stock, df)
    except Exception:
        pass

    await db.flush()
    return records


async def _parse_ths_financials(db: AsyncSession, stock: Stock, df) -> list[FinancialData]:
    records = []
    for _, row in df.tail(12).iterrows():
        period_val = row.get("报告期", "")
        period = str(period_val)
        # THS returns year like 2024, convert to date format
        if len(period) == 4 and period.isdigit():
            period = f"{period}-12-31"
        elif len(period) > 10:
            period = period[:10]
        if not period or period == "None":
            continue

        result = await db.execute(
            select(FinancialData).where(
                FinancialData.stock_id == stock.id,
                FinancialData.period == period,
            )
        )
        if result.scalars().first():
            continue

        fd = FinancialData(
            stock_id=stock.id,
            period=period,
            roe=_parse_percent(row.get("净资产收益率")),
            gross_margin=_parse_percent(row.get("销售毛利率")),
            net_margin=_parse_percent(row.get("销售净利率")),
            eps=_parse_amount(row.get("基本每股收益")),
            revenue=_parse_amount(row.get("营业总收入")),
            net_profit=_parse_amount(row.get("净利润")),
        )
        db.add(fd)
        records.append(fd)

    return records


async def _parse_indicator_financials(db: AsyncSession, stock: Stock, df) -> list[FinancialData]:
    records = []
    for _, row in df.head(6).iterrows():
        period = str(row.get("日期", ""))[:10]
        if not period or period == "None":
            continue

        result = await db.execute(
            select(FinancialData).where(
                FinancialData.stock_id == stock.id,
                FinancialData.period == period,
            )
        )
        if result.scalars().first():
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

    return records


def _parse_amount(val) -> float | None:
    """Parse amounts like '4.88亿', '56.84亿', '2300万'."""
    if val is None or val == "-" or val == "" or val is False:
        return None
    s = str(val).strip()
    try:
        if s.endswith("亿"):
            return float(s[:-1]) * 100000000
        elif s.endswith("万"):
            return float(s[:-1]) * 10000
        elif s.endswith("%"):
            return float(s[:-1])
        return float(s)
    except (ValueError, TypeError):
        return None


def _parse_percent(val) -> float | None:
    """Parse percentage values like '12.5%' or just '12.5'."""
    if val is None or val == "-" or val == "" or val is False:
        return None
    s = str(val).strip().replace("%", "")
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _safe_float(val) -> float | None:
    if val is None or val == "-" or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
