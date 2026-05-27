import json
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.research_report import ResearchReport

MIAOXIANG_URL = "https://ai-saas.eastmoney.com/proxy/b/mcp/tool/searchNews"


async def search_reports(query: str, page: int = 1, page_size: int = 10) -> list[dict]:
    headers = {"em_api_key": settings.em_api_key, "Content-Type": "application/json"}
    payload = {"query": query, "page": page, "pageSize": page_size}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(MIAOXIANG_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    inner = data.get("data", {}).get("llmSearchResponse", {})
    if isinstance(inner, str):
        inner = json.loads(inner)

    items = inner.get("data", [])
    results = []
    for item in items:
        results.append({
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "date": item.get("date", ""),
            "content": item.get("content", ""),
            "jump_url": item.get("jumpUrl", ""),
        })
    return results


async def fetch_and_save_reports(
    db: AsyncSession, query: str, target_type: str = "industry",
    stock_id: int | None = None, industry_id: int | None = None,
) -> list[ResearchReport]:
    reports_data = await search_reports(query)
    saved = []

    for r in reports_data:
        if not r["title"]:
            continue

        result = await db.execute(
            select(ResearchReport).where(
                ResearchReport.title == r["title"],
                ResearchReport.source == r["source"],
            )
        )
        if result.scalars().first():
            continue

        report = ResearchReport(
            target_type=target_type,
            stock_id=stock_id,
            industry_id=industry_id,
            source=r["source"],
            title=r["title"],
            report_date=r["date"],
            content=r["content"],
        )
        db.add(report)
        saved.append(report)

    await db.flush()
    return saved
