# default
from typing import Annotated

# libraries
from fastapi import APIRouter, Depends

# local
from core.models import UserDailyStudyTimes
from api.schemas import UserStatsGetQuery, UserStatsGetResponse

router = APIRouter()


@router.get("/user_stats")
async def user_stats(
    params: Annotated[dict, Depends(UserStatsGetQuery)],
) -> UserStatsGetResponse:
    return await UserDailyStudyTimes.get_user_study_time_stats(params.user_discord_id)
