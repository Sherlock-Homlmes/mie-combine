# lib
import motor.motor_asyncio

# local
from core.env import env


client = motor.motor_asyncio.AsyncIOMotorClient(env.DATABASE_URL)
