# default
import datetime
from typing import Optional

# lib
from beanie import Document, Link

# local
from .users import Users


class BadUsers(Document):
    user: Link[Users]
    bad_content: str
    diary_message_id: Optional[int] = None

    created_at: datetime.datetime
