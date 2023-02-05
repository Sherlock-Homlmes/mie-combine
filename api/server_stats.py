# local
from .app import app
from bot.features.schedule.static_channels import discord_server_info


@app.get("/server-info")
def get_server_info():
    return discord_server_info()
