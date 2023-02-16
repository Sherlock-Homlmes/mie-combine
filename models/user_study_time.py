# default
import datetime

# lib
from beanie import Document, Link

# local
from .users import Users


class UserStudyTime(Document):

    user: Link[Users]
    study_time: int
    last_studied_at: datetime.datetime
