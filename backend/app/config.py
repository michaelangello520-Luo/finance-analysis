from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/finance.db"
    em_api_key: str = ""

    llm_provider: str = "deepseek"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-v4-pro"

    glm_api_key: str = ""
    glm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    glm_model: str = "glm-5.1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
