# default
import datetime

# lib
from beanie import Document, Link

# local
from .users import Users


class VoiceChannels(Document):
    owner: Link[Users]
    vc_id: int

    created_at: datetime.datetime
