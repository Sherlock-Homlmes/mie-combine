# default
import datetime

# lib
from beanie import Document, Link

# local
from .users import Users
from other_modules.time_modules import vn_now


class VoiceChannels(Document):

    owner: Link[Users]
    vc_id: str
    cc_id: str

    created_at: datetime.datetime = vn_now()
