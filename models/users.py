# default
import datetime
from typing import Optional

from beanie import Document

# lib
from pydantic import BaseModel


class UserMetadata(BaseModel):
    bank_account: Optional[str] = None
    bank_code: Optional[str] = None
    disable_achievement_role: Optional[bool] = False


class Users(Document):
    discord_id: int
    name: str
    nick: Optional[str] = None
    avatar: str
    is_in_server: bool = True
    is_bot: bool = False

    metadata: Optional[UserMetadata] = None

    created_at: datetime.datetime
    joined_at: datetime.datetime
    leaved_at: Optional[datetime.datetime] = None

    def update_metadata(self, data: dict):
        if self.metadata:
            self.metadata = self.metadata.model_copy(update=data)
        else:
            self.metadata = UserMetadata(**data)
