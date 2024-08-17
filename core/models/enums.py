# default
from enum import Enum


class TopicEnum(Enum):
    ENG = "etopic"
    VIE = "vtopic"


class BanFormEnum(Enum):
    WARN = "warn"
    MUTE = "mute"
    BAN = "ban"
