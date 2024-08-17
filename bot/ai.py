import re

import google.generativeai as genai
from core.conf.bot.conf import bot

from core.env import env
from other_modules.image_handle import delete_image, save_image

genai.configure(api_key=env.GEMINI_AI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@bot.listen()
async def on_message(message):
    if not message.author.bot and bot.user.mentioned_in(message):
        async with message.channel.typing():
            message_without_mention = (
                re.sub(r"<@.*?>", "", message.content) + "\n Answer in Vietnamese. No yapping"
            )
            contents = None
            if len(message.attachments):
                try:
                    file = await save_image(message.attachments[0].url)
                    f = genai.upload_file(file)
                    contents = [message_without_mention, f]
                except Exception:
                    await message.channel.send(
                        "Xảy ra lỗi trong quá trình xử lý", reference=message
                    )
                    return
                finally:
                    delete_image(file)
            else:
                contents = message_without_mention

            response = model.generate_content(contents)
            await message.channel.send(response.text, reference=message)
