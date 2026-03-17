from datetime import datetime
from typing import Annotated, Optional

from beanie import Document, Indexed
from pydantic import Field

from utils.time_modules import Now


class ExtractFileRecords(Document):
    """Tracks uploaded files in R2 and their embed status."""

    user_discord_id: Annotated[int, Indexed()]
    channel_id: int
    guild_id: Optional[int] = None

    original_filename: str
    s3_key: str
    file_content: str | None = None
    confidence: float

    uploaded_at: datetime = Field(default_factory=lambda: Now().now)
