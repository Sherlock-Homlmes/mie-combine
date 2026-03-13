import re
import traceback

import discord
import google.generativeai as genai
from google.api_core.exceptions import PermissionDenied

from core.conf.bot.conf import bot
from models import AIMessageAuthor
from utils.image_handle import delete_image, save_image
from utils.ai_coversation import aclient

from . import gemini_service, history_service, memory_service


DISCORD_MAX_LENGTH_MESSAGE = 2000


@bot.listen()
async def on_message(message):
    await bot._fully_ready.wait()

    if message.author.bot or (
        (
            not bot.user.mentioned_in(message)
            or isinstance(message.channel, discord.DMChannel)
        )
        and not (
            message.position == 0
            and message.channel.parent
            and message.channel.parent.name == "giúp-đỡ-học-tập"
        )
    ):
        return
    try:
        # if message.attachments:
        # await handle_attachments(message)
        await handle_chat(message)
        await bot.process_commands(message)
    except Exception:
        await message.reply("Mie đang lỗi rồi bạn thử lại sau nhé!")
        traceback.print_exc()

    # if bot.user.mentioned_in(message) or (
    #     message.position == 0
    #     and message.channel.parent
    #     and message.channel.parent.name == "giúp-đỡ-học-tập"
    # ):
    #     async with message.channel.typing():
    #         chat.history = await UserAIChatHistory.get_history(
    #             message.author.id, message.channel.id
    #         )
    #         message_without_mention = re.sub(r"<@.*?>", "\n", message.content)
    #         # message.channel.parent is currently error
    #         # if message.channel.parent and message.channel.parent.name == "giúp-đỡ-học-tập":
    #         #     message_without_mention = f"{message.channel.name}\n{message_without_mention}"
    #         contents = [
    #             message_without_mention,
    #         ]
    #         if len(message.attachments):
    #             try:
    #                 file = await save_image(message.attachments[0].url)
    #                 f = genai.upload_file(file)
    #                 contents.append(f)
    #                 # files = [await save_image(f) for f in message.attachments]
    #                 # fs = [genai.upload_file(f) for f in files]
    #                 # contents.extend(fs)
    #             except Exception:
    #                 await message.channel.send(
    #                     "Xảy ra lỗi trong quá trình xử lý", reference=message
    #                 )
    #                 return
    #             finally:
    #                 # for file in files:
    #                 delete_image(file)

    #         async def try_call_ai(without_files=[]):
    #             try:
    #                 chat.history = await UserAIChatHistory.get_history(
    #                     message.author.id,
    #                     message.channel.id,
    #                     without_files=without_files,
    #                 )
    #                 response = await chat.send_message_async(contents)
    #                 return response.text
    #             except PermissionDenied as e:
    #                 pattern = r"File (\w+) or"
    #                 match = re.search(pattern, str(e))
    #                 file_id = match.group(1)
    #                 print("AI files removed: ", file_id)
    #                 without_files.append(file_id)
    #                 return await try_call_ai(without_files)

    #         sucess = True
    #         try:
    #             text = await try_call_ai()
    #         except Exception as e:
    #             print("AI error: ", e)
    #             text = (
    #                 "Xảy ra lỗi trong quá trình xử lý. Liên hệ Admin để được trợ giúp"
    #             )
    #             sucess = False

    #         if len(text) > DISCORD_MAX_LENGTH_MESSAGE:
    #             first_part = text[:DISCORD_MAX_LENGTH_MESSAGE]
    #             second_part = text[DISCORD_MAX_LENGTH_MESSAGE:]

    #             await message.channel.send(first_part, reference=message)
    #             await message.channel.send(second_part)
    #         else:
    #             await message.channel.send(text, reference=message)

    #         if not sucess:
    #             return
    #         return

    #         # TODO: refactor
    #         # model_contents = []
    #         # if chat.history[-2].role != "user":
    #         #     return
    #         # ai_model_contents = chat.history[-2].parts
    #         # for content in ai_model_contents:
    #         #     if content.text:
    #         #         model_contents.append(Content(text=content.text))
    #         #     elif content.file_data:
    #         #         model_contents.append(
    #         #             Content(
    #         #                 file_data=FileData(
    #         #                     mime_type=content.file_data.mime_type,
    #         #                     file_uri=content.file_data.file_uri,
    #         #                 )
    #         #             )
    #         #         )
    #         # # insert content
    #         # await UserAIChatHistory(
    #         #     model_type=model_type,
    #         #     created_by=message.author.id,
    #         #     channel_id=message.channel.id,
    #         #     contents=model_contents,
    #         #     response=response.text,
    #         # ).insert()


# async def handle_attachments(message: discord.Message):
#     user_id = str(message.author.id)
#     guild_id = str(message.guild.id) if message.guild else "dm"
#     channel_id = str(message.channel.id)
#     cache_file_folder_path = "assets/cache/"

#     async with message.channel.typing():
#         for attachment in message.attachments:
#             if attachment.size > settings.max_file_size_bytes:
#                 await message.reply(
#                     f"❌ `{attachment.filename}` quá lớn "
#                     f"({attachment.size / 1024 / 1024:.1f}MB). "
#                     f"Max: {settings.max_file_size_mb}MB"
#                 )
#                 continue
#             file_name = random_filename_from_url(attachment.url)
#             file_path = await save_image(
#                 attachment.url, cache_file_folder_path + file_name
#             )
#             if not file_path:
#                 raise Exception("Can not download file")
#             mime = attachment.content_type or "application/octet-stream"

#             # Nếu là ảnh thì extract text bằng Gemini Vision trước
#             extracted = None
#             if mime.startswith("image/"):
#                 extracted = await file_service.extract_image_text(file_path)
#                 await history_service.add_message(
#                     user_id, channel_id, guild_id, "user", extracted
#                 )
#             else:
#                 await message.reply("Hiện tại Mie chưa hỗ trợ định dạng file này")
#                 return


async def handle_chat(message: discord.Message, override_content: str = None):
    user_id = str(message.author.id)
    guild_id = str(message.guild.id) if message.guild else "dm"
    channel_id = str(message.channel.id)
    content = (
        override_content or message.content.replace(f"<@{bot.user.id}>", "").strip()
    )

    if not content:
        return

    async with message.channel.typing():
        try:
            history = await history_service.get_recent_messages(user_id, channel_id)
            facts = await memory_service.get_user_facts(user_id)

            response = await gemini_service.generate_response(
                user_message=content,
                history=history,
                user_facts=facts,
                user_id=user_id,
                guild_id=guild_id,
                username=message.author.display_name,
            )

            await history_service.add_message(
                user_id, channel_id, guild_id, AIMessageAuthor.USER, content
            )
            await history_service.add_message(
                user_id, channel_id, guild_id, AIMessageAuthor.ASSISTANT, response
            )

            updated_history = await history_service.get_recent_messages(
                user_id, channel_id, limit=6
            )
            await memory_service.extract_and_store_facts(
                user_id, guild_id, updated_history
            )

            # Send (split nếu quá 1900 ký tự)
            parts = [response[i : i + 1900] for i in range(0, len(response), 1900)]
            for i, part in enumerate(parts):
                if i == 0:
                    await message.reply(part)
                else:
                    await message.channel.send(part)

        except Exception as e:
            traceback.print_exc()
            await message.reply(f"⚠️ Lỗi: `{type(e).__name__}: {e}`")
