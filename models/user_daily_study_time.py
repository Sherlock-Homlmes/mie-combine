# default
import datetime
from typing import List

import pymongo

# lib
from beanie import Document, Indexed, Link
from pydantic import validator

# local
from .users import Users


class UserDailyStudyTime(Document):

    user: Link[Users]
    study_time: List[int]
    """
        Study time type = List[time: int] (24 elements)
    """
    date: Indexed(datetime.datetime, index_type=pymongo.DESCENDING)

    class Settings:
        validate_on_save = True

    @validator("study_time")
    def studytime_must_lt_60_and_gt_0(cls, value):
        for index, val in enumerate(value):
            if val < 0:
                # print(value, val)
                value[index] = 0
                # raise ValueError("Study time must greater than 0")
            elif val > 60:
                # print(value, val)
                value[index] = 60
                # raise ValueError("Study time must greater than 0")
        return value

    @validator("study_time")
    def studytime_must_have_24_elements(cls, value):
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
