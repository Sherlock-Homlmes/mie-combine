from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class ENVEnum(str, Enum):
    DEV = "DEV"
    PROD = "PROD"


class Env(BaseSettings):
    BOT_ONLY: bool = False
    BOT_TOKEN: str
    DATABASE_URL: str
    GEMINI_AI_API_KEY: str
    GEMINI_MODEL: str = "gemini-flash-latest"
    GEMINI_LITE_MODEL: str = "gemini-flash-lite-latest"
    GEMINI_EMBED_MODEL: str = "gemini-embedding-2-preview"
    CLOUDFLARE_API_KEY: str | None = None
    CLOUDFLARE_ACCOUNT_ID: str | None = None
    CLOUDFLARE_GUARD_MODEL: str = "@cf/meta/llama-3.1-8b-instruct-fast"
    CLOUDFLARE_ROUTING_MODEL: str = "@cf/meta/llama-3.1-8b-instruct-fast"
    CLOUDFLARE_FUNCTION_MODEL: str = "@cf/zai-org/glm-4.7-flash"
    # ZAI_AI_API_KEY: str
    OOPS_WEBHOOK_URL: str | None = None
    ENV: ENVEnum = ENVEnum.PROD

    model_config = SettingsConfigDict(env_file=".env")


env = Env()
is_dev_env = env.ENV == ENVEnum.DEV
