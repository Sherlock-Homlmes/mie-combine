from .color import *
from .topic import *
from .game_center import *
from .welcome import *

from bot import bot


@bot.listen()
async def on_ready():
    print("4.Errand ready")
