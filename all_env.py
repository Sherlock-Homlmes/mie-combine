import os
from dotenv import load_dotenv

load_dotenv()

database = True
my_secret = os.environ.get("bot_token")
database_url = os.environ.get("database_url")
