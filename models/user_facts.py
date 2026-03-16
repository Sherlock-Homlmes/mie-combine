from datetime import datetime
from enum import Enum
from typing import Annotated

from beanie import Document, Indexed
from pydantic import BaseModel, Field

from utils.time_modules import vn_now


class UserFactHistory(BaseModel):
    value: str
    original_message: str
    timestamp: datetime = Field(default_factory=vn_now)


class FactSourceEnum(str, Enum):
    EXPLICIT = "explicit"  # nói thẳng
    INFERRED = "inferred"  # suy luận


class UserFactCategoryEnum(str, Enum):
    PREFERENCE = "preference"
    SKILL = "skill"
    PERSONAL = "personal"
    HABIT = "habit"
    GOAL = "goal"
    KNOWLEDGE = "knowledge"
    STRUGGLE = "struggle"
    PROGRESS = "progress"
    CONTEXT = "context"


class UserFacts(Document):
    user_discord_id: Annotated[int, Indexed()]
    category: UserFactCategoryEnum
    key: str
    confidence: float
    source: FactSourceEnum
    value: str
    created_at: datetime = Field(default_factory=vn_now)
    updated_at: datetime = Field(default_factory=vn_now)
    history: list[UserFactHistory] = Field(default_factory=list)
