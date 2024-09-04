from .bad_users import BadUsers
from .confessions import ConfessionReply, Confessions, ConfessionStatusEnum, ConfessionTypeEnum
from .enums import *
from .errand_data import ErrandData
from .user_daily_study_time import UserDailyStudyTime
from .user_study_sections import UserStudySection
from .users import Users
from .voice_channels import VoiceChannels

document_models = [
    Confessions,
    Users,
    ErrandData,
    BadUsers,
    VoiceChannels,
    UserDailyStudyTime,
    UserStudySection,
]
