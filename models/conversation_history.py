from datetime import datetime
from enum import Enum
from typing import Annotated

import pymongo
from beanie import Document, Indexed
from pydantic import BaseModel, Field

from utils.time_modules import Now


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageEntry(BaseModel):
    role: Role
    content: str
    created_at: datetime = Field(default_factory=lambda: Now().now)
    attachments: list[str] = Field(default_factory=list)


class ConversationHistory(Document):
    """Stores last N messages per user per channel."""

    user_discord_id: Annotated[int, Indexed()]
    channel_id: Annotated[int, Indexed()]
    guild_id: int | None = None

    messages: list[MessageEntry] = Field(default_factory=list)

    updated_at: datetime = Field(default_factory=lambda: Now().now)
    created_at: datetime = Field(default_factory=lambda: Now().now)

    class Settings:
        indexes = [
            pymongo.IndexModel(
                [
                    ("user_discord_id", pymongo.ASCENDING),
                    ("channel_id", pymongo.ASCENDING),
                ],
                unique=True,
            )
        ]
