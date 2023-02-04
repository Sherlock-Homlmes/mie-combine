import os
from dotenv import load_dotenv

load_dotenv()

database = True
environment = os.environ.get("environment")
my_secret = os.environ.get("BOT_TOKEN")
database_url = os.environ.get("database_url")
