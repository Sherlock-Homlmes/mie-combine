import os

# environment = "replit"
environment = "local"
if environment == "local":
	from dotenv import load_dotenv
	load_dotenv()

my_secret = os.environ.get('BOT_TOKEN')
database_url = os.environ.get('database_url')

from pymongo import MongoClient
cluster = MongoClient(database_url)
dtbs = cluster["discord_betterme"]