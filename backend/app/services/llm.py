import json
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings as app_settings


PROVIDER_CONFIG = {
    "deepseek": {
        "base_url_env": "deepseek_base_url",
        "api_key_env": "deepseek_api_key",
        "model_env": "deepseek_model",
    },
    "glm": {
        "base_url_env": "glm_base_url",
        "api_key_env": "glm_api_key",
        "model_env": "glm_model",
    },
}


async def get_llm_config(db: AsyncSession) -> dict:
    from app.models.settings import Setting

    result = await db.execute(
        select(Setting).where(Setting.key == "llm_provider")
    )
    row = result.scalar_one_or_none()
    provider = row.value if row else app_settings.llm_provider

    provider = provider if provider in PROVIDER_CONFIG else "deepseek"
    cfg = PROVIDER_CONFIG[provider]

    return {
        "provider": provider,
        "base_url": getattr(app_settings, cfg["base_url_env"]),
        "api_key": getattr(app_settings, cfg["api_key_env"]),
        "model": getattr(app_settings, cfg["model_env"]),
    }


async def set_llm_provider(db: AsyncSession, provider: str) -> dict:
    from app.models.settings import Setting

    if provider not in PROVIDER_CONFIG:
        raise ValueError(f"Unknown provider: {provider}")

    result = await db.execute(
        select(Setting).where(Setting.key == "llm_provider")
    )
    row = result.scalar_one_or_none()
    if row:
        row.value = provider
    else:
        db.add(Setting(key="llm_provider", value=provider))
    await db.commit()

    return await get_llm_config(db)


async def chat_completion(
    db: AsyncSession,
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    config = await get_llm_config(db)

    url = f"{config['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"]
