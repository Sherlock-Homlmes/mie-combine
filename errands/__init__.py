from .color import *
from .topic import *
from .game_center import *
from .study_club import *
from .chatbot_resource import *
from .welcome import *
from .feedback import *

from base import bot
@bot.listen()
async def on_ready():
    print('3.Errand ready')
