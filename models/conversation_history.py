from typing import Annotated
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field, BaseModel
from datetime import datetime
from typing import Optional
import pymongo


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageEntry(BaseModel):
    role: Role
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attachments: list[str] = Field(default_factory=list)


class ConversationHistory(Document):
    """Stores last N messages per user per channel."""

    user_discord_id: Annotated[int, Indexed()]
    guild_id: Optional[str] = None
    channel_id: Annotated[int, Indexed()]

    messages: list[MessageEntry] = Field(default_factory=list)

    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "conversation_history"
        indexes = [
            pymongo.IndexModel(
                [
                    ("user_discord_id", pymongo.ASCENDING),
                    ("channel_id", pymongo.ASCENDING),
                ],
                unique=True,
            )
        ]
