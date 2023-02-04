# default
import datetime
from typing import Optional

# lib
from beanie import Document


class Users(Document):

    discord_id: str
    name: str
    avatar: str
    is_in_server: bool = True

    created_at: datetime.datetime
    joined_at: datetime.datetime
    leaved_at: Optional[datetime.datetime] = None
