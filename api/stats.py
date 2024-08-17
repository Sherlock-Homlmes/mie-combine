# libraries
from fastapi import APIRouter

# local
from bot.schedule.static_channels import discord_server_info
from fastapi.responses import ORJSONResponse

# create all api routers
router = APIRouter()


@router.get("/stats")
def server_stats():
    return ORJSONResponse(discord_server_info())
