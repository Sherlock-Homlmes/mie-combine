from datetime import datetime
from typing import Annotated, Optional

from beanie import Document, Indexed
from pydantic import Field

from utils.time_modules import vn_now


class ExtractFileRecords(Document):
    """Tracks uploaded files in R2 and their embed status."""

    user_discord_id: Annotated[int, Indexed()]
    guild_id: Optional[int] = None
    channel_id: int

    original_filename: str
    s3_key: str  # e.g. {uuid}.pdf
    file_content: str = None

    uploaded_at: datetime = Field(default_factory=vn_now)
