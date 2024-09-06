import datetime
from enum import Enum
from typing import List, Optional, Union

from beanie import Document, Insert, UnionDoc, before_event
from pydantic import BaseModel

from other_modules.time_modules import Now


class ConfessionTypeEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class ConfessionStatusEnum(str, Enum):
    OPEN = "open"
    CLOSE = "close"


class ConfessionReply(BaseModel):
    created_by: int
    member_index: int
    content: str

    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class Confessions(UnionDoc):
    class Settings:
        name = "Confessions"  # Collection name
        class_id = "_class_id"  # _class_id is default beanie internal field used to filter children Documents


class OpenConfessions(Document):
    channel_id: int
    created_by: int
    type: ConfessionTypeEnum
    created_at: Optional[datetime.datetime] = None

    class Settings:
        union_doc = Confessions

    ### Events
    @before_event(Insert)
    async def set_created_at(self):
        now = Now().now
        self.created_at = now


class CloseConfessions(OpenConfessions):
    index: int
    channel_id: Union[int, None] = None
    created_by: int

    type: ConfessionTypeEnum

    content: str
    message_id: int
    thread_id: int
    manage_thread_id: int
    thread_replies: List[ConfessionReply] = []

    updated_at: Optional[datetime.datetime] = None

    class Settings:
        union_doc = Confessions
