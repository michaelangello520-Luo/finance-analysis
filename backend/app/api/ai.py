import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stock import Stock
from app.models.research_report import ResearchReport
from app.services.llm import chat_completion

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AnalyzeStockRequest(BaseModel):
    stock_code: str


class AnalyzeReportRequest(BaseModel):
    report_id: int


STOCK_ANALYSIS_PROMPT = """你是一位专业的A股长期投资分析师。请基于以下数据，给出结构化的投资分析。

## 股票基本信息
{stock_info}

## 最近财务数据
{financial_data}

## 相关研报摘要
{reports_summary}

请按以下结构输出（使用中文）：

### 投资评级
（买入/增持/中性/减持/卖出，附一句话理由）

### 核心优势
（列出2-3个关键竞争优势）

### 主要风险
（列出2-3个主要风险因素）

### 行业地位
（在产业链中的位置和竞争力）

### 长期投资建议
（200字以内的长期投资建议，包含合理的估值区间参考）

⚠️ 免责声明：以上分析仅基于公开数据和AI模型生成，不构成投资建议。投资有风险，入市需谨慎。"""


REPORT_ANALYSIS_PROMPT = """你是一位专业的证券研报分析师。请对以下研报进行深度解读。

## 研报信息
标题：{title}
来源：{source}
日期：{date}

## 研报正文
{content}

请按以下结构输出（使用中文）：

### 核心观点
（3-5句话概括研报核心论点）

### 关键数据
（列出研报中最重要的3-5个数据点）

### 产业链分析
（上游/中游/下游相关环节和公司）

### 投资建议
（研报给出的投资建议和目标价位）

### 风险提示
（研报提到的风险因素）

⚠️ 免责声明：以上分析为AI对研报的解读，可能存在理解偏差，仅供参考。"""


async def _get_stock_data(db: AsyncSession, stock_code: str) -> dict:
    from app.models.financial_data import FinancialData
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Stock)
        .options(selectinload(Stock.financial_data), selectinload(Stock.industry))
        .where(Stock.code == stock_code)
    )
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")

    report_result = await db.execute(
        select(ResearchReport)
        .where(ResearchReport.stock_id == stock.id)
        .order_by(ResearchReport.report_date.desc())
        .limit(5)
    )
    reports = report_result.scalars().all()

    industry_name = "未知"
    if stock.industry:
        industry_name = stock.industry.name
    stock_info = f"代码: {stock.code}, 名称: {stock.name}, 行业: {industry_name}"

    financial_data = "暂无财务数据"
    if stock.financial_data:
        fd = stock.financial_data[0]
        financial_data = (
            f"营收: {fd.revenue or 'N/A'}亿, 净利润: {fd.net_profit or 'N/A'}亿, "
            f"ROE: {fd.roe or 'N/A'}%, 毛利率: {fd.gross_margin or 'N/A'}%, "
            f"净利率: {fd.net_margin or 'N/A'}%, EPS: {fd.eps or 'N/A'}, "
            f"PE: {fd.pe or 'N/A'}, PB: {fd.pb or 'N/A'}"
        )

    reports_summary = ""
    for r in reports:
        reports_summary += f"- [{r.report_date or '未知'}] {r.title} ({r.institution or '未知机构'})\n"
    if not reports_summary:
        reports_summary = "暂无相关研报"

    return {
        "stock_info": stock_info,
        "financial_data": financial_data,
        "reports_summary": reports_summary,
        "stock": stock,
    }


@router.post("/analyze-stock")
async def analyze_stock(
    body: AnalyzeStockRequest, db: AsyncSession = Depends(get_db)
):
    data = await _get_stock_data(db, body.stock_code)

    prompt = STOCK_ANALYSIS_PROMPT.format(
        stock_info=data["stock_info"],
        financial_data=data["financial_data"],
        reports_summary=data["reports_summary"],
    )

    messages = [
        {"role": "system", "content": "你是一位专业的A股长期投资分析师，擅长基本面分析和行业研究。"},
        {"role": "user", "content": prompt},
    ]

    analysis = await chat_completion(db, messages, temperature=0.3, max_tokens=4096)

    return {
        "stock_code": body.stock_code,
        "stock_name": data["stock"].name,
        "analysis": analysis,
    }


@router.post("/analyze-report")
async def analyze_report(
    body: AnalyzeReportRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ResearchReport).where(ResearchReport.id == body.report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {body.report_id} not found")

    prompt = REPORT_ANALYSIS_PROMPT.format(
        title=report.title,
        source=report.institution or "未知",
        date=report.report_date or "未知",
        content=(report.content or "")[:8000],
    )

    messages = [
        {"role": "system", "content": "你是一位专业的证券研报分析师，擅长解读券商研究报告。"},
        {"role": "user", "content": prompt},
    ]

    analysis = await chat_completion(db, messages, temperature=0.3, max_tokens=4096)

    return {
        "report_id": body.report_id,
        "report_title": report.title,
        "analysis": analysis,
    }
