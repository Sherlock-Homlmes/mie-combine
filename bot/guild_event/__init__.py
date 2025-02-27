from .on_member_join import *
from .on_member_leave import *
from .on_member_update import *


from core.conf.bot.conf import bot


@bot.listen()
async def on_ready():
    print("2.Guild event ready")
