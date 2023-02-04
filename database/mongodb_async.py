import motor.motor_asyncio

from all_env import database_url

client = motor.motor_asyncio.AsyncIOMotorClient(database_url)
