# default
import datetime
from typing import Optional

# lib
from beanie import Document


class Users(Document):
    discord_id: int
    name: str
    nick: Optional[str] = None
    avatar: str
    is_in_server: bool = True
    is_bot: bool = False

    created_at: datetime.datetime
    joined_at: datetime.datetime
    leaved_at: Optional[datetime.datetime] = None
