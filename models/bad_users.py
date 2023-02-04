# default
import datetime

# lib
from beanie import Document, Link

# local
from .users import Users
from feature_func.time_modules import vn_now


class BadUsers(Document):

    user: Link[Users]
    bad_content: str

    created_at: datetime.datetime = vn_now()
