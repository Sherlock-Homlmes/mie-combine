from base import (
  # necess
  bot,tasks,get,
  # var
  color_roles
  )

import json
import random

from feature_func.stable_json import open_database

@bot.command(name="etopic")
async def etopic(ctx):
  topic = random.choice(open_database("/topic/etopic"))
  await ctx.send(f"Chủ đề: **{topic}**")

@bot.command(name="vtopic")
async def etopic(ctx):
  topic = random.choice(open_database("/topic/vtopic"))
  await ctx.send(f"Chủ đề: **{topic}**")