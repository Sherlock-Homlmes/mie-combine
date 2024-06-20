from pydantic_settings import BaseSettings


class Env(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str


env = Env()
