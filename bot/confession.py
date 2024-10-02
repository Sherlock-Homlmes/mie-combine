# default
import asyncio
from dataclasses import dataclass
from typing import Optional, Union

# library
import discord
from discord import ui
from discord.ext.commands import context, has_permissions

from bot.security.bad_words_check import check_bad_words

# local
from core.conf.bot.conf import bot, guild_id, server_info
from core.models import CloseConfessions, ConfessionReply, ConfessionTypeEnum, OpenConfessions
from utils.discord_bot.channel_name import rewrite_confession_channel_name
from utils.image_handle import delete_image, save_image
from utils.time_modules import Now

confession_thread_ids = []


# Create choose confession message
class ConfessionOption(ui.View):
    @ui.select(
        placeholder="Lựa chọn",
        options=[
            discord.SelectOption(
                label="Confession ẩn danh",
                value="private-confession",
                description="Nơi bạn tâm sự những câu chuyện thầm kín",
            ),
            discord.SelectOption(
                label="Confession công khai",
                value="public-confession",
                description="Nơi bạn tâm sự những câu chuyện thầm kín",
            ),
        ],
    )
    async def select_callback(self, select, interaction):
        pass


class ConfessionPrivateReplyButton(ui.View):
    @ui.button(label="Trả lời ẩn danh", custom_id="private-reply-confession")
    async def select_callback(self, interaction, button):
        pass


class ConfessionPrivateReplyModal(ui.Modal, title="Questionnaire Response"):
    content = ui.TextInput(label="Nội dung", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        if not check_bad_words(str(self.content)):
            (
                await interaction.response.send_message(
                    f"**Vui lòng không sử dụng từ nhạy cảm trong câu của bạn**\n**Nội dung:** {str(self.content)}",
                    ephemeral=True,
                ),
            )
            return

        cfs = await CloseConfessions.find_one(CloseConfessions.message_id == interaction.message.id)
        if interaction.user.id == cfs.created_by:
            member_index = 0
        else:
            other_thread_replies = [
                reply.member_index
                for reply in cfs.thread_replies
                if reply.created_by != interaction.user.id
            ]
            if not len(cfs.thread_replies):
                member_index = 1
            elif len(cfs.thread_replies) != len(other_thread_replies):
                member_index = [
                    reply.member_index
                    for reply in cfs.thread_replies
                    if reply.created_by == interaction.user.id
                ][0]
            else:
                member_index = max(other_thread_replies) + 1
        thread_reply = ConfessionReply(
            created_by=interaction.user.id,
            member_index=member_index,
            content=str(self.content),
            created_at=Now().now,
        )
        cfs.thread_replies.append(thread_reply)
        guild = bot.get_guild(guild_id)
        thread = guild.get_thread(cfs.thread_id)
        manage_thread = guild.get_thread(cfs.manage_thread_id)
        await asyncio.gather(
            *[
                cfs.save(),
                thread.send(
                    f"**Từ: Người ẩn danh {member_index}**\n{self.content}"
                    if member_index
                    else f"**Từ: Chủ post**\n{self.content}"
                ),
                manage_thread.send(
                    f"**Từ: Người ẩn danh {member_index}** <@{interaction.user.id}>\n{self.content}",
                ),
                interaction.response.send_message("Đã gửi tin nhắn ẩn danh", ephemeral=True),
            ]
        )


@bot.listen()
async def on_ready():
    print("5.Confession ready")
    await asyncio.sleep(10)
    await fix_confession()


@bot.command(name="confession")
@has_permissions(administrator=True)
async def confession_choose(ctx: context.Context):
    view = ConfessionOption()
    await ctx.message.delete()
    await ctx.send(view=view)


# confession process
@dataclass
class Confession:
    # default value
    channel: discord.TextChannel
    member: Optional[Union[discord.Member, discord.User]]
    cfs_type: ConfessionTypeEnum

    # value create when processing
    files: list
    content: str = ""
    model: OpenConfessions = None
    is_sended: bool = False

    async def set_confession(self):
        # insert confession to database
        await OpenConfessions(
            channel_id=self.channel.id,
            created_by=self.member.id,
            type=self.cfs_type,
        ).insert()

        # send help messsage to channel
        embed = discord.Embed(
            title="**Nơi " + self.member.name + " tâm sự những câu chuyện thầm kín**",
            description="Chúng mình luôn lắng nghe và chia sẻ mọi buồn vui cùng bạn",
            colour=discord.Colour.gold(),
        )
        embed.add_field(
            name="**Chú ý**",
            value="Kênh sẽ biến mất sau 30 phút hoặc bạn gõ lệnh ``/end_confession`` ",
            inline=False,
        )
        embed.set_footer(text="""BetterMe - Better everyday""")
        await self.channel.send(content=self.member.mention, embed=embed)

        # wait 30 minutes
        await asyncio.sleep(1800)

        if await OpenConfessions.find_one(OpenConfessions.channel_id == self.channel.id):
            await self.channel.send(
                self.member.mention
                + "**Những lời tâm tư ngàn lời không nói hết. Nếu bạn muốn tiếp tục tâm sự hãy tạo 1 kênh mới. Kênh này sẽ biến mất sau 2 phút nữa. **"  # noqa: E501
            )
            await asyncio.sleep(120)
        await asyncio.sleep(10)

    async def text_process(self):
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(self.channel.id)
        messages = [message async for message in channel.history(limit=200)]
        messages.reverse()
        for message in messages:
            if message.author.id == self.member.id:
                if message.content not in ["", "m,end", "M,end", "/end_confession"]:
                    self.content += message.content + ". "
                if message.attachments:
                    for attach in message.attachments:
                        image = await save_image(attach.url)
                        self.files.append(image)

    async def send_files(self):
        files_to_read: list[str] = self.files
        files_to_send: list[discord.File] = []

        for filename in files_to_read:
            with open(filename, "rb") as f:
                files_to_send.append(discord.File(f))
            delete_image(filename)
        return files_to_send

    async def end_confession(self):
        confession = await OpenConfessions.find_one(OpenConfessions.channel_id == self.channel.id)
        if confession:
            await self.text_process()
            try:
                self.model = confession
                if len(self.content) == 0 and self.files == []:
                    message = None
                elif len(self.content) < 50 and self.files == []:
                    message = "Nội dung confession của bạn rất ngắn nên sẽ không được gửi đi. Lưu ý: nếu gửi confession khó hiểu, không có chủ đích sẽ bị mute ít nhất 3 ngày"  # noqa: E501
                else:
                    await self.send_confession()
                    message = "Cảm ơn bạn đã chia sẻ cùng chúng mình"
                    self.is_sended = True

                if not self.is_sended:
                    await confession.delete()
                await self.channel.delete()
                if message:
                    await self.member.send(message)
            except discord.errors.HTTPException:
                await self.channel.send(
                    "Confession quá dài. Hãy đảm bảo confession của bạn không quá 4000 kí tự."
                )

    async def send_confession(self):
        confession_count = await CloseConfessions.find_all().max(CloseConfessions.index) or 0
        confession_count += 1
        files = await self.send_files()

        content = f"``` Confession {confession_count}-ẩn danh```"
        embed = discord.Embed(
            title="**Tâm sự ẩn danh**",
            description=self.content,
            colour=discord.Colour.gold(),
        )
        embed.set_footer(text="""BetterMe - Better everyday""")
        if self.model.type == ConfessionTypeEnum.PUBLIC:
            embed.add_field(name="**Id**", value=f"||{self.member.mention}||", inline=False)
            embed.set_thumbnail(url=self.member.avatar or self.member.default_avatar.url)
        message = await server_info.confession_channel.send(
            content=content, embed=embed, files=files, view=ConfessionPrivateReplyButton()
        )
        thread = await message.create_thread(name="Rep confession ở đây nè!!!")
        if self.model.type == ConfessionTypeEnum.PRIVATE:
            embed.add_field(name="**Id**", value=f"||{self.member.mention}||", inline=False)
            embed.set_thumbnail(url=self.member.avatar or self.member.default_avatar.url)
        manage_message = await server_info.manage_confession_channel.send(
            content=content, embed=embed, files=files
        )
        manage_thread = await manage_message.create_thread(name="Rep confession")
        await asyncio.gather(
            *[
                CloseConfessions(
                    index=confession_count,
                    content=self.content,
                    message_id=message.id,
                    thread_id=thread.id,
                    manage_thread_id=manage_thread.id,
                    type=self.model.type,
                    created_by=self.model.created_by,
                ).insert(),
                self.model.delete(),
            ]
        )


# end confession
@bot.tree.command(name="end_confession", description="Kết thúc confession")
async def end_confession(interaction: discord.Interaction):
    await interaction.response.defer()
    confession = await OpenConfessions.find_one(
        OpenConfessions.channel_id == interaction.channel.id
    )
    if confession:
        confession = Confession(
            channel=interaction.channel,
            member=await interaction.guild.fetch_member(confession.created_by),
            cfs_type=confession.type,
            files=[],
        )
        await confession.end_confession()
    else:
        await interaction.response(
            "Hãy gõ lệnh này trong kênh confession của bạn",
        )


# REFACTOR: not using on_interaction
@bot.listen()
async def on_interaction(interaction: discord.Interaction):
    if interaction.data.get("custom_id") == "private-reply-confession":
        await interaction.response.send_modal(ConfessionPrivateReplyModal())
    elif interaction.message:
        if (
            interaction.message.id == server_info.confession_dropdown_id
            and interaction.type == discord.InteractionType.component
        ):
            await interaction.response.defer()
            member = interaction.user
            values = interaction.data["values"]

            # Not allow create confession if that member already have exist confession
            if await OpenConfessions.find_one(OpenConfessions.created_by == member.id):
                await member.send("Bạn chỉ có thể tạo 1 kênh confession 1 lúc")
            elif "private-confession" in values or "public-confession" in values:
                chanel_name = rewrite_confession_channel_name(member.name, "confession")

                channel = await interaction.channel.category.create_text_channel(
                    chanel_name,
                    overwrites={
                        interaction.guild.default_role: discord.PermissionOverwrite(
                            view_channel=False
                        ),
                        member: discord.PermissionOverwrite(view_channel=True),
                    },
                    reason=None,
                )

                # confession
                if "private-confession" in values:
                    cfs_type = ConfessionTypeEnum.PRIVATE
                elif "public-confession" in values:
                    cfs_type = ConfessionTypeEnum.PUBLIC

                confession = Confession(channel=channel, member=member, cfs_type=cfs_type, files=[])
                await confession.set_confession()
                await confession.end_confession()


async def fix_confession():
    now = Now().now
    async for confession_data in OpenConfessions.find():
        channel: discord.TextChannel
        member: discord.Member | discord.User
        channel, member = await asyncio.gather(
            *[
                server_info.guild.fetch_channel(confession_data.channel_id),
                server_info.guild.fetch_member(confession_data.created_by),
            ]
        )
        # delete if confession channel last longer than 40 minutes
        if channel and (now - channel.created_at).seconds >= 2400:
            await Confession(
                channel=channel,
                member=member,
                cfs_type=confession_data.type,
                files=[],
            ).end_confession()
    print("fix confession done")
