from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenRouter (acts as unified gateway to open-source LLMs)
    openrouter_api_key: str = "demo"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # Using mistralai/mistral-7b-instruct — free tier on OpenRouter, fast, good at structured tasks
    openrouter_model: str = "meta-llama/llama-3.2-3b-instruct"
   

    # App behaviour
    app_env: str = "development"
    mock_mode: bool = False          # skip AI calls; use deterministic mock responses
    cache_ttl_seconds: int = 3600    # TTL for in-memory LRU cache

    # Optional USDA key — gracefully falls back to internal dataset if absent
    usda_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
