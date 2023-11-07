# lib
import beanie
import motor.motor_asyncio

# local
from core.env import env
from models import (
    Users,
    BadUsers,
    Confessions,
    ErrandData,
    VoiceChannels,
    UserDailyStudyTime,
    UserStudySection,
)

client = motor.motor_asyncio.AsyncIOMotorClient(env.DATABASE_URL)


async def connect_to_database():
    await beanie.init_beanie(
        database=client.discord_betterme,
        document_models=[
            Users,
            BadUsers,
            Confessions,
            ErrandData,
            VoiceChannels,
            UserDailyStudyTime,
            UserStudySection,
        ],
    )
    print("Beanie-Mongodb connected successfully")
