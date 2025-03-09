# default
import datetime
from typing import List, Optional

import pymongo

# lib
from beanie import Document, Indexed
from pydantic import validator
from cache import AsyncTTL

# local
from api.schemas import UserStatsGetResponse, DataUserDailyStudyTime


class UserDailyStudyTimes(Document):
    user_discord_id: Indexed(int, index_type=pymongo.DESCENDING)
    """
        Study time type = List[time: int] (24 elements)
    """
    study_time: List[int]
    date: Indexed(datetime.datetime, index_type=pymongo.DESCENDING)

    class Settings:
        validate_on_save = True
        indexes = [
            [
                ("user_discord_id", pymongo.DESCENDING),
                ("date", pymongo.DESCENDING),
            ],
        ]

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
    @AsyncTTL(time_to_live=60)
    async def get_user_study_time_stats(
        user_discord_id: int,
        from_date: Optional[datetime.datetime] = None,
        to_date: Optional[datetime.datetime] = None,
    ) -> UserStatsGetResponse:
        queries = {"user_discord_id": user_discord_id}
        date_queries = {}
        if from_date:
            date_queries["$gte"] = from_date
        if to_date:
            date_queries["$lte"] = to_date
        if len(date_queries.keys()):
            queries["date"] = date_queries
        user_daily_study_time = (
            await UserDailyStudyTimes.find(queries).project(DataUserDailyStudyTime).to_list()
        )
        total_time = sum([sum(x.study_time) for x in user_daily_study_time])
        if not total_time:
            total_time = 0
        return UserStatsGetResponse(
            user_discord_id=user_discord_id,
            daily_study_time=user_daily_study_time,
            total=total_time,
        )
