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
    ENV: ENVEnum = ENVEnum.PROD

    model_config = SettingsConfigDict(env_file=".env")


env = Env()
is_dev_env = env.ENV == ENVEnum.DEV
