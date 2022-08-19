import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
from discord_slash import SlashCommand

import datetime

####### BOT #######

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["M,", "m,"], intents=intents)
slash = SlashCommand(bot, sync_commands=True)


@bot.listen()
async def on_ready():
    #start
    print('We have logged in as {0.user} combine bot'.format(bot))


####### VAR #######

### Started: Discord
guild_id = 880360143768924210
admin_id = [880359404036317215, 278423331026501633]
### Part 1: SCHEDULE
# 1.1:static_channels
thpt_channel_id = 894578663893389403
cap3_channel_id = 894578664300249159
thptday = datetime.datetime(2023, 7, 7)
cap3day = datetime.datetime(2023, 6, 6)
total_mem_channel_id = 933534750386307102
online_mem_channel_id = 933534913347584081
study_count_channel_id = 925813858105430046

### Part 3: ERRANDS
# 3.1: color
color_roles = [
    909419355127816242, 909418177178529812, 909420197390196826,
    909418887853010964, 909420320996335636, 909418878306750514,
    909414569921904690, 914494643671015484, 915929478260195368,
    885803187410464788, 915934631566643221
]
# 3.2: game center
khu_vui_choi = 923963988784590920
# 3.3: bot resources
bot_resource_channel_id = 1007151133439033374

### Part 4: Easter Egg
easter_eggs_id = 1005365132546822184
# 4.1: Homie
homie_id = 882810518400798750
# 4.2: Love sick eyes
lovesick_id = 998642382083985621

### Part 5: Confession
# 5.1: dropdown
confession_dropdown_id = 927991226920222831
confession_category_id = 902499044356657173
confession_channel_id = 925086728497291394
private_confession_channel_id = 925790946971508806

####### IMPORT MODULES #######
from schedule import *
from security import *
from errands import *
from easter_eggs import *
from confession import *
from create_vc import *

# from test import *
