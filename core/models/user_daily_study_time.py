# default
import datetime
from typing import List, Optional

import pymongo

# lib
from beanie import Document, Indexed
from pydantic import validator

# local
from api.schemas import UserStatsGetResponse, DataUserDailyStudyTime


class UserDailyStudyTimes(Document):
    user_discord_id: int
    """
        Study time type = List[time: int] (24 elements)
    """
    study_time: List[int]
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
    async def get_user_study_time_stats(
        user_discord_id: int,
        from_date: Optional[datetime.datetime] = None,
        to_date: Optional[datetime.datetime] = None,
    ):
        user_daily_study_time = (
            await UserDailyStudyTimes.find(UserDailyStudyTimes.user_discord_id == user_discord_id)
            .project(DataUserDailyStudyTime)
            .to_list()
        )
        total_time = sum([sum(x.study_time) for x in user_daily_study_time])
        if not total_time:
            total_time = 0
        return UserStatsGetResponse(
            user_discord_id=user_discord_id,
            daily_study_time=user_daily_study_time,
            total=total_time,
        )
