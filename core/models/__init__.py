import beanie

from core.database.mongodb import client

from .bad_users import BadUsers
from .confessions import (
    CloseConfessions,
    ConfessionReply,
    Confessions,
    ConfessionStatusEnum,
    ConfessionTypeEnum,
    OpenConfessions,
)
from .enums import *
from .errand_data import ErrandData
from .user_daily_study_time import UserDailyStudyTimes
from .user_study_sections import UserStudySection
from .user_ai_chat_history import UserAIChatHistory, Content, FileData
from .users import Users
from .voice_channels import VoiceChannels

document_models = [
    Confessions,
    CloseConfessions,
    OpenConfessions,
    Users,
    ErrandData,
    BadUsers,
    VoiceChannels,
    UserStudySection,
    UserDailyStudyTimes,
    UserAIChatHistory,
]


async def connect_db() -> None:
    print("Connecting to database...")
    await beanie.init_beanie(
        database=client.discord_betterme,
        document_models=document_models,
    )
    print("Connect to database success")
