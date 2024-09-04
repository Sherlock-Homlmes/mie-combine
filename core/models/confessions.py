from enum import Enum
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel


class ConfessionTypeEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class ConfessionStatusEnum(str, Enum):
    OPEN = "open"
    CLOSE = "close"


class ConfessionReply(BaseModel):
    member_id: str
    member_position: int
    content: str


class Confessions(Document):
    channel_id: int
    member_id: int

    type: ConfessionTypeEnum
    status: ConfessionStatusEnum = ConfessionStatusEnum.OPEN

    confession_index: Optional[int] = None
    content: Optional[str] = None
    thread_id: Optional[int] = None
    manage_thread_id: Optional[int] = None
    thread_replies: List[ConfessionReply] = []
