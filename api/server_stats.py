# libraries
from fastapi import APIRouter

# local
from bot.schedule.static_channels import discord_server_info

# create all api routers
router = APIRouter()


@router.get("/server_stats")
def server_stats():
    return discord_server_info()
