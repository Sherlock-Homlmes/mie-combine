import os
from dotenv import load_dotenv

load_dotenv()

database = True
environment = os.environ.get("environment")
my_secret = os.environ.get("BOT_TOKEN")
database_url = os.environ.get("database_url")

# from pymongo import MongoClient

# cluster = MongoClient(database_url)
# dtbs = cluster["discord_betterme"]
# dtb = dtbs["errand_data"]


# def open_database(data_key):
#     return dtb.find_one({"name": data_key})["value"]
