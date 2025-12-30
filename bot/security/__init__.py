from .introduce import *
from .cam_check import *
from .bad_words_check import *

from core.conf.bot.conf import bot


@bot.listen()
async def on_ready():
    await bot._fully_ready.wait()
    print("3.Security ready")
