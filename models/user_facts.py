from typing import Annotated
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field, BaseModel
from datetime import datetime


class UserFactHistory(BaseModel):
    value: str
    original_message: str
    at: datetime = Field(default_factory=datetime.utcnow)


class FactSource(str, Enum):
    EXPLICIT = "explicit"  # nói thẳng
    INFERRED = "inferred"  # suy luận


class UserFacts(Document):
    user_discord_id: Annotated[int, Indexed()]
    category: str
    key: str
    confidence: float
    source: FactSource
    value: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    history: list[UserFactHistory] = Field(default_factory=list)
