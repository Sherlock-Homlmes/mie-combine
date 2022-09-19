from base import (
  # necess
  bot,tasks,get,
  # var
  color_roles
  )

import json
import random

from feature_func.stable_json import open_database

@bot.tree.command(name="etopic", description="Gợi ý 1 topic tiếng Anh")
async def etopic(ctx):
  topic = random.choice(open_database("/topic/etopic"))
  await ctx.send(f"Chủ đề: **{topic}**")

@bot.tree.command(name="vtopic", description="Gợi ý 1 topic tiếng Việt")
async def vtopic(ctx):
  topic = random.choice(open_database("/topic/vtopic"))
  await ctx.send(f"Chủ đề: **{topic}**")