import asyncio
import traceback

import discord
from pydantic import BaseModel

from core.conf.bot.conf import bot
from models import AIMessageAuthor
from utils.image_handle import delete_image, random_filename_from_url, save_image

from . import (
    file_service,
    gemini_service,
    history_service,
    memory_service,
    rate_limit_service,
    routing_service,
)

DISCORD_MAX_LENGTH_MESSAGE = 2000


@bot.listen()
async def on_message(message):
    await bot._fully_ready.wait()

    if (
        message.author.bot
        or (
            not bot.user.mentioned_in(message)
            or isinstance(message.channel, discord.DMChannel)
        )
        # and not (
        #     message.position == 0
        #     and message.channel.parent
        #     and message.channel.parent.name == "giúp-đỡ-học-tập"
        # )
    ):
        return
    # Check rate limit
    allowed, _ = await rate_limit_service.check_rate_limit(message.author)
    if not allowed:
        limit = rate_limit_service.get_limit(message.author)
        await message.reply(
            f"⛔ Bạn đã dùng hết limit {limit} lần ngày hôm nay rồi. Mai bạn thử lại hoặc nâng cấp lên Server Booster để có thêm limit nhé!"
        )
        return

    # Handle attachments and messages
    try:
        # attachment_handler = await handle_attachments(message)
        # if not attachment_handler.success:
        #     await message.reply(attachment_handler.reason)
        #     return
        await handle_chat(message)
        await bot.process_commands(message)
    except Exception:
        await message.reply("Mie đang lỗi rồi bạn thử lại sau nhé!")
        traceback.print_exc()


class AttachmentHandler(BaseModel):
    success: bool
    reason: str | None = None


async def handle_attachments(message: discord.Message) -> AttachmentHandler:
    if not message.attachments:
        return AttachmentHandler(success=True)

    user_id = message.author.id
    guild_id = message.guild.id
    channel_id = message.channel.id
    cache_file_folder_path = "assets/cache/"

    try:
        file_service.check_file_validation(message.attachments)
    except Exception as e:
        return AttachmentHandler(success=False, reason=str(e))

    async with message.channel.typing():
        for attachment in message.attachments:
            file_name = random_filename_from_url(attachment.url)
            file_path = await save_image(
                attachment.url, cache_file_folder_path + file_name
            )
            if not file_path:
                raise Exception("Can not download file")
            mime = attachment.content_type or "application/octet-stream"

            # Image
            extracted: file_service.OCRResponse | None = None
            if mime.startswith("image/"):
                extracted = await file_service.extract_image_to_text(file_path)
                print(extracted)
                if (
                    extracted.confidence
                    < file_service.IMAGE_EXTRACT_CONFIDENCE_THRESHOLD
                ):
                    return AttachmentHandler(
                        success=False,
                        reason="Bot không thể lấy được nội dung từ ảnh của bạn. Bạn có thể thử  chụp lại với ảnh khác hoặc gửi dưới dạng văn bản nhé!",
                    )
                else:
                    await asyncio.gather(
                        file_service.add_file_record(
                            user_id,
                            channel_id,
                            guild_id,
                            file_path,
                            attachment.filename,
                            extracted.confidence,
                            extracted.value,
                        ),
                        history_service.add_message(
                            user_id, channel_id, guild_id, "user", extracted.value
                        ),
                    )
                    return AttachmentHandler(success=True)
            # Other file type
            else:
                return AttachmentHandler(
                    success=False, reason="Hiện tại Mie chưa hỗ trợ định dạng file này"
                )


async def handle_chat(message: discord.Message, override_content: str = None):
    user_discord_id = message.author.id
    guild_id = message.guild.id
    channel_id = message.channel.id
    content = (
        override_content
        or message.content.replace(f"<@{bot.user.id}>", "").replace("  ", " ").strip()
    )

    if not content:
        return

    async with message.channel.typing():
        try:
            # Route message to appropriate model
            try:
                has_attachments = len(message.attachments) > 0
                model_type = await routing_service.classify_message_complexity(
                    content, has_attachments
                )
            except Exception:
                traceback.print_exc()
                model_type = routing_service.COMPLEX

            history = await history_service.get_recent_messages(
                user_discord_id, channel_id, guild_id, limit=10
            )
            facts = await memory_service.get_user_facts(
                user_discord_id, only_strong_fact=True
            )

            response = await gemini_service.generate_response(
                discord_message=message,
                user_message=content,
                history=history,
                user_facts=facts,
                user_id=user_discord_id,
                username=message.author.display_name,
                model_type=model_type,
            )
            if response.startswith("[TOOLS USE]:"):
                response = response.replace("[TOOLS USE]:", "", 1).strip()
            else:
                response = handle_response_message(response)
                await history_service.add_message(
                    user_discord_id, channel_id, guild_id, AIMessageAuthor.USER, content
                )
                await history_service.add_message(
                    user_discord_id,
                    channel_id,
                    guild_id,
                    AIMessageAuthor.ASSISTANT,
                    response,
                )

                updated_history = await history_service.get_recent_messages(
                    user_discord_id, channel_id, guild_id, limit=6
                )
                await memory_service.extract_and_store_facts(
                    user_discord_id, updated_history
                )

            # Send (split nếu quá 1900 ký tự)
            parts = [response[i : i + 1900] for i in range(0, len(response), 1900)]
            for i, part in enumerate(parts):
                if i == 0:
                    await message.reply(part)
                else:
                    await message.channel.send(part)

        except Exception:
            traceback.print_exc()
            await message.reply("Bot đang lỗi rồi bạn sửa lại sau nhé")


def handle_response_message(message: str):
    result = message.replace("@everyone", " everyone").replace("@here", " here")
    return result
