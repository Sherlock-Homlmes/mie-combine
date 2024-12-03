import re

import google.generativeai as genai

from core.conf.bot.conf import bot
from core.env import env
from utils.image_handle import delete_image, save_image
from core.models import UserAIChatHistory, Content, FileData

genai.configure(api_key=env.GEMINI_AI_API_KEY)
model_type = "gemini-1.5-flash"
model = genai.GenerativeModel(model_type)


@bot.listen()
async def on_message(message):
    if message.author.bot:
        return

    if bot.user.mentioned_in(message) or (
        message.position == 0
        and message.channel.parent
        and message.channel.parent.name == "giúp-đỡ-học-tập"
    ):
        async with message.channel.typing():
            chat = model.start_chat()
            chat.history = await UserAIChatHistory.get_history(
                message.author.id, message.channel.id
            )
            message_without_mention = (
                re.sub(r"<@.*?>", "\n", message.content) + "\n Answer in Vietnamese. No yapping"
            )
            # message.channel.parent is currently error
            # if message.channel.parent and message.channel.parent.name == "giúp-đỡ-học-tập":
            #     message_without_mention = f"{message.channel.name}\n{message_without_mention}"
            contents = [
                message_without_mention,
            ]
            if len(message.attachments):
                try:
                    file = await save_image(message.attachments[0].url)
                    f = genai.upload_file(file)
                    contents.append(f)
                    # files = [await save_image(f) for f in message.attachments]
                    # fs = [genai.upload_file(f) for f in files]
                    # contents.extend(fs)
                except Exception:
                    await message.channel.send(
                        "Xảy ra lỗi trong quá trình xử lý", reference=message
                    )
                    return
                finally:
                    # for file in files:
                    delete_image(file)

            response = await chat.send_message_async(contents)
            await message.channel.send(response.text, reference=message)

            # TODO: refactor
            model_contents = []
            if chat.history[-2].role != "user":
                return
            ai_model_contents = chat.history[-2].parts
            for content in ai_model_contents:
                if content.text:
                    model_contents.append(Content(text=content.text))
                elif content.file_data:
                    model_contents.append(
                        Content(
                            file_data=FileData(
                                mime_type=content.file_data.mime_type,
                                file_uri=content.file_data.file_uri,
                            )
                        )
                    )
            # insert content
            await UserAIChatHistory(
                model_type=model_type,
                created_by=message.author.id,
                channel_id=message.channel.id,
                contents=model_contents,
                response=response.text,
            ).insert()
