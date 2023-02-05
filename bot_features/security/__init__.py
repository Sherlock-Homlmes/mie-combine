from .introduce import *
from .cam_check import *
from .bad_words_check import *

from base import bot


@bot.listen()
async def on_ready():
    print("3.Security ready")
