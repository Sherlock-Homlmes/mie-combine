import os

# environment = "replit"
environment = "heroku"
database = True

###
if environment != "replit":
	from dotenv import load_dotenv
	load_dotenv()

my_secret = os.environ.get('BOT_TOKEN')
database_url = os.environ.get('database_url')

status = os.environ.get('STATUS')

if database:
	from pymongo import MongoClient
	cluster = MongoClient(database_url)
	dtbs = cluster["discord_betterme"]