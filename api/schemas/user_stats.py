from typing import Optional, List
import datetime
from pydantic import BaseModel, model_validator


class UserStatsGetQuery(BaseModel):
    user_discord_id: int
    from_date: Optional[datetime.datetime] = None
    to_date: Optional[datetime.datetime] = None

    @model_validator(mode="before")
    def from_must_before_to(cls, values):
        if (
            values.get("from_date")
            and values.get("to_date")
            and values.get("from_date") > values.get("to_date")
        ):
            raise ValueError("To date must greater than from date")
        return values


class DataUserDailyStudyTime(BaseModel):
    study_time: List[int]
    date: datetime.datetime


class UserStatsGetResponse(BaseModel):
    user_discord_id: int
    total: int
    daily_study_time: List[DataUserDailyStudyTime]
    # total_this_month: int
    # total_this_week: int
