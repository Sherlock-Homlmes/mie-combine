import re

import google.generativeai as genai

from core.conf.bot.conf import bot
from core.env import env
from other_modules.image_handle import delete_image, save_image

genai.configure(api_key=env.GEMINI_AI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@bot.listen()
async def on_message(message):
    if message.author.bot:
        return
    if any(
        bot.user.mentioned_in(message),
        message.channel.parent and message.channel.parent.name == "giúp-đỡ-học-tập",
    ):
        async with message.channel.typing():
            message_without_mention = (
                message.channel.name
                + "\n"
                + re.sub(r"<@.*?>", "\n", message.content)
                + "\n Answer in Vietnamese. No yapping"
            )
            contents = None
            if len(message.attachments):
                try:
                    # file = await save_image(message.attachments[0].url)
                    # f = genai.upload_file(file)
                    files = [await save_image(f) for f in message.attachments]
                    fs = [genai.upload_file(f) for f in files]
                    contents = [
                        message_without_mention,
                    ]
                    contents.extend(fs)
                except Exception:
                    await message.channel.send(
                        "Xảy ra lỗi trong quá trình xử lý", reference=message
                    )
                    return
                finally:
                    for file in files:
                        delete_image(file)
            else:
                contents = message_without_mention
            response = model.generate_content(contents)
            print(response.text)
            await message.channel.send(response.text, reference=message)
