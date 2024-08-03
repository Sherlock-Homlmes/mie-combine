import re

import google.generativeai as genai
from bot import bot

from core.env import env

genai.configure(api_key=env.GEMINI_AI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@bot.listen()
async def on_message(message):
    if not message.author.bot and bot.user.mentioned_in(message):
        async with message.channel.typing():
            message_without_mention = re.sub(r"<@.*?>", "", message.content)
            response = model.generate_content(message_without_mention + "\n Answer in Vietnamese")
            await message.channel.send(response.text, reference=message)
