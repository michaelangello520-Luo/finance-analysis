from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.llm import get_llm_config, set_llm_provider

router = APIRouter(prefix="/api/settings", tags=["settings"])


class LLMProviderUpdate(BaseModel):
    provider: str


@router.get("/llm")
async def get_llm_settings(db: AsyncSession = Depends(get_db)):
    config = await get_llm_config(db)
    return {
        "provider": config["provider"],
        "model": config["model"],
        "available_providers": [
            {"name": "deepseek", "model": "deepseek-v4-pro"},
            {"name": "glm", "model": "glm-5.1"},
        ],
    }


@router.put("/llm")
async def update_llm_settings(
    body: LLMProviderUpdate, db: AsyncSession = Depends(get_db)
):
    config = await set_llm_provider(db, body.provider)
    return {
        "provider": config["provider"],
        "model": config["model"],
        "message": f"已切换到 {config['provider']} ({config['model']})",
    }
