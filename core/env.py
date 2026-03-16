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
    # ZAI_AI_API_KEY: str
    OOPS_WEBHOOK_URL: str | None = None
    ENV: ENVEnum = ENVEnum.PROD

    model_config = SettingsConfigDict(env_file=".env")


env = Env()
is_dev_env = env.ENV == ENVEnum.DEV
