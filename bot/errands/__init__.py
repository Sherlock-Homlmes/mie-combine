from .color import *
from .topic import *
from .game_center import *
from .welcome import *

from core.conf.bot.conf import bot


@bot.listen()
async def on_ready():
    await bot._fully_ready.wait()
    print("4.Errand ready")
