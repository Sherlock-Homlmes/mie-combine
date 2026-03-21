# AI layers:
# Layer 1: Check if user is disabled from using AI
# Layer 2: Rate limit
# Layer 3: Guard service protect model from harmful content
# Layer 4: Handle attachments (if any)
# Layer 5: Classify content and complexity
# Layer 6: Generate content
# Layer 7: Store fact from content

import asyncio
import traceback

import discord
from pydantic import BaseModel

from core.conf.bot.conf import bot, server_info
from models import AIMessageAuthor
from utils.image_handle import delete_image, random_filename_from_url, save_image

from . import (
    content_generate_service,
    file_service,
    guard_service,
    history_service,
    memory_service,
    rate_limit_service,
    routing_service,
)

DISCORD_MAX_LENGTH_MESSAGE = 2000


async def send_guard_violation_log(message: discord.Message, violation_content: str):
    """Send violation log to ai_logs channel"""

    if not server_info.channels.ai_logs:
        return

    embed = discord.Embed(
        title="🚨 AI Guard Violation Detected",
        description="A user attempted to send a message that violated AI safety guidelines.",
        color=discord.Color.red(),
    )

    embed.add_field(
        name="👤 User",
        value=f"{message.author.mention} (`{message.author.id}`)",
        inline=True,
    )
    embed.add_field(
        name="📍 Channel",
        value=f"{message.channel.mention} (`{message.channel.id}`)",
        inline=True,
    )
    embed.add_field(
        name="📝 Violating Content",
        value=f"```\n{violation_content[:500]}```"
        if len(violation_content) > 500
        else f"```\n{violation_content}\n```",
        inline=False,
    )
    embed.add_field(
        name="🔗 Message Link",
        value=f"[Jump to Message]({message.jump_url})",
        inline=False,
    )

    view = guard_service.GuardViolationView()

    try:
        await server_info.channels.ai_logs.send(embed=embed, view=view)
    except Exception as e:
        print(f"Failed to send guard violation log: {e}")


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

    # Layer 1: Check if user is disabled from using AI
    is_disabled = await guard_service.check_user_disabled(message.author.id)
    if is_disabled:
        await message.reply(
            "⛔ Bạn đã bị vô hiệu hóa tính năng AI. Nếu bạn nghĩ đây là lỗi, hãy liên hệ admin."
        )
        return

    # Layer 2: Rate limit
    allowed, _ = await rate_limit_service.check_rate_limit(message.author)
    if not allowed:
        limit = rate_limit_service.get_limit(message.author)
        await message.reply(
            f"⛔ Bạn đã dùng hết limit {limit} lần ngày hôm nay rồi. Mai bạn thử lại hoặc nâng cấp lên Server Booster để có thêm limit nhé!"
        )
        return

    # Get message content
    content = handle_request_message(message.content)

    if not content:
        return

    # Layer 3: Guard service protect model from harmful content
    guard_result = await guard_service.message_guard(content)
    if guard_result == guard_service.GuardResult.BLOCKED:
        await send_guard_violation_log(message, content)
        await message.reply(
            "⛔ Tin nhắn của bạn có thể đang vi phạm chính sách sử dụng AI. Vui lòng thử lại. Nếu bạn nghĩ đây là lỗi, hãy liên hệ admin."
        )
        return

    try:
        # Layer 4: Handle attachments (if any)
        # attachment_handler = await handle_attachments(message)
        # if not attachment_handler.success:
        #     await message.reply(attachment_handler.reason)
        #     return
        # Handle chat message
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


async def handle_chat(message: discord.Message):
    user_discord_id = message.author.id
    guild_id = message.guild.id
    channel_id = message.channel.id
    content = handle_request_message(message.content)

    if not content:
        return

    async with message.channel.typing():
        try:
            # Layer 5: Classify content and complexity to route to the right model
            try:
                routing_result = await routing_service.route_message(content)
                model_type = routing_result.complexity
                purpose = routing_result.purpose
                print("------------------------")
                print("Routing: ", routing_result)
            except Exception:
                raise Exception("Phân loại tin nhắn thất bại")

            # Layer 6: Generate content
            history = await history_service.get_recent_messages(
                user_discord_id, channel_id, guild_id, limit=8
            )
            facts = await memory_service.get_user_facts(
                user_discord_id, only_strong_fact=True
            )

            response = await content_generate_service.generate_response(
                discord_message=message,
                user_message=content,
                history=history,
                user_facts=facts,
                user_id=user_discord_id,
                username=message.author.display_name,
                model_type=model_type,
                purpose=purpose,
            )
            if purpose != "FUNC_CALL":
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

                # Layer 7: Store fact from content
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


def handle_request_message(message: str):
    content = message.replace(f"<@{bot.user.id}>", "").replace("  ", " ").strip()
    return content


def handle_response_message(message: str):
    result = message.replace("@everyone", " everyone").replace("@here", " here")
    return result
