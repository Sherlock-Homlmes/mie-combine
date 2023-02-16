# default
import datetime

# lib
from beanie import Document, Link

# local
from .users import Users


class BadUsers(Document):

    user: Link[Users]
    bad_content: str

    created_at: datetime.datetime
