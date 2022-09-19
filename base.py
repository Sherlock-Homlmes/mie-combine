import discord
from discord import (
    Interaction,
    app_commands
)
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions, context
from discord.utils import get
from discord.ui import View, Select

import datetime

####### BOT #######
guild_id = 880360143768924210
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix = ["m,","M,"], intents = intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral = True)
bot = Bot()


@bot.listen()
async def on_ready():
    #start
    print('We have logged in as {0.user} combine bot'.format(bot))


####### VAR #######

### Started: Discord
guild_id = 880360143768924210
admin_id = [880359404036317215, 278423331026501633]
muted_id = 890553937445408839
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

### Part 6: Create voice channel
channel_cre = {
  #test
#   "1021296228585185280":{
#     "category_id": 917405878217490482,
#     "locate": "SG",
#     "limit": (2,15)
#   },

  #real
  "918549426732142653":{
    "category_id": 900439704950956053,
    "locate": "SG",
    "limit": (3,15)
  },
  "918549341948497961":{
    "category_id": 901518444271386694,
    "locate": "CP",
    "limit": (2,2)
  },
  "918549182107746356":{
    "category_id": 900598666572750929,
    "locate": "SA",
    "limit": (1,1)
  },
  "922461169799790642":{
    "category_id": 915512539733975050,
    "locate": "CR",
    "limit": (1,99)
  },
  "923964509935243265":{
    "category_id": 902499044356657173,
    "locate": "Tâm sự",
    "limit": (1,99)
  }

}

####### IMPORT MODULES #######
from schedule import *
from security import *
from errands import *
from easter_eggs import *
from confession import *
from create_vc import *

# from test import *
