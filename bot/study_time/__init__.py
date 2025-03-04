from core.conf.bot.conf import bot
from .study_time_log import *
from .statistic import *


@bot.listen()
async def on_ready():
    print("7.Study time ready")
