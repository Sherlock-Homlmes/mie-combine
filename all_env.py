import os
from dotenv import load_dotenv

load_dotenv()

my_secret: str = os.environ.get("bot_token")
database_url: str = os.environ.get("database_url")
bot_only: bool = os.environ.get("bot_only", default=False)
