from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):
    BOT_ONLY: bool = True
    BOT_TOKEN: str
    DATABASE_URL: str
    GEMINI_AI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


env = Env()
