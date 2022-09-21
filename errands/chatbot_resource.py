from base import (
  # necess
  bot,tasks,get,discord,
  #var
  bot_resource_channel_id
)

import json

from feature_func.mongodb.ai_chatbot import create_data
from easter_eggs.homie import update_homie

ai_chatbot_data = []

@bot.listen()
async def on_message(message: discord.Message):
  global ai_chatbot_data

  if message.author.bot == False and message.content != "":
    data = (message.author.id, message.content)
    ai_chatbot_data.append(data)

    if len(ai_chatbot_data) >= 1000:
      create_data(ai_chatbot_data)
      await update_homie(ai_chatbot_data)

      channel = get(bot.get_all_channels(), id=bot_resource_channel_id)
      with open('data.json', 'w', encoding='utf-8') as f1:
        json.dump(ai_chatbot_data, f1, ensure_ascii=False, indent=4)
      with open('data.json', 'rb') as f2:
        await channel.send(file=discord.File(f2))

      ai_chatbot_data = None
      ai_chatbot_data =[]
