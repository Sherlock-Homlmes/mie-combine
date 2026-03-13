from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional


class ExtractFileRecords(Document):
    """Tracks uploaded files in R2 and their embed status."""

    user_discord_id: Annotated[int, Indexed()]
    guild_id: Optional[str] = None
    channel_id: str

    original_filename: str
    s3_key: str  # e.g. {uuid}.pdf
    file_content: str = None

    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
