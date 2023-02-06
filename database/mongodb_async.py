# lib
import beanie
import motor.motor_asyncio

# local
from all_env import database_url
from models import *

client = motor.motor_asyncio.AsyncIOMotorClient(database_url)


async def connect_to_database():
    await beanie.init_beanie(
        database=client.discord_betterme,
        document_models=[Users, BadUsers, Confessions, ErrandData, VoiceChannels],
    )
    print("Beanie-Mongodb connected successfully")
