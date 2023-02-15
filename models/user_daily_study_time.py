# default
from typing import List
from pydantic import validator
import datetime

# lib
from beanie import Document, Link

# local
from .users import Users
from other_modules.time_modules import Now


class UserDailyStudyTime(Document):

    user: Link[Users]
    study_time: List[int]
    date: datetime.datetime = Now().today

    @validator("study_time")
    def studytime_must_lt_60_and_gt_0(cls, value):
        for index, val in enumerate(value):
            if val < 0:
                raise ValueError("Study time must greater than 0")
            elif val > 60:
                raise ValueError("Study time must greater than 0")
        return value

    @validator("study_time")
    def studytime_length_must_equal_24(cls, value):
        if len(value) != 24:
            raise ValueError("Study time length must equal 24")
        return value

    @staticmethod
    async def get_user_total_study_time(user_id: int):
        user_daily_study_time = await UserDailyStudyTime.find(
            UserDailyStudyTime.user.discord_id == str(user_id), fetch_links=True
        ).to_list()
        total_time = sum([sum(x.study_time) for x in user_daily_study_time])
        if not total_time:
            total_time = 0
        return total_time
