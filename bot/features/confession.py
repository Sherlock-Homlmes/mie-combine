# default
import asyncio
import datetime
from dataclasses import dataclass
from typing import Optional, Union

# library
import discord
from discord.ext.commands import context, has_permissions
from discord.ui import View

# local
from bot import bot, guild_id, server_info
from models import Confessions, ErrandData
from other_modules.discord_bot.channel_name import rewrite_confession_channel_name
from other_modules.image_handle import delete_image, save_image


# Create choose confession message
class ConfessionOption(View):
    @discord.ui.select(
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
    cfs_type: str

    # value create when processing
    files: list
    content: str = ""

    async def set_confession(self):
        # insert confession to database
        confession = Confessions(
            channel_id=self.channel.id, member_id=self.member.id, type=self.cfs_type
        )
        await confession.insert()

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

        if await Confessions.find_one(Confessions.channel_id == str(self.channel.id)):
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
                        image = save_image(attach.url)
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
        confession = await Confessions.find_one(
            Confessions.channel_id == str(self.channel.id)
        )
        if confession:
            await self.text_process()
            try:
                if len(self.content) == 0 and self.files == []:
                    message = None
                elif len(self.content) < 50 and self.files == []:
                    message = "Nội dung confession của bạn rất ngắn nên sẽ không được gửi đi. Lưu ý: nếu gửi confession khó hiểu, không có chủ đích sẽ bị mute ít nhất 3 ngày"  # noqa: E501
                else:
                    if self.cfs_type == "private":
                        await self.send_private_confession()
                    elif self.cfs_type == "public":
                        await self.send_public_confession()

                    server_info_data = await ErrandData.find_one(
                        ErrandData.name == "server_info"
                    )
                    server_info_data.value["confession_count"] += 1
                    server_info.confession_count = server_info_data.value[
                        "confession_count"
                    ]
                    await server_info_data.save()

                    message = "Cảm ơn bạn đã chia sẻ cùng chúng mình"

                await confession.delete()
                await self.channel.delete()
                if message:
                    await self.member.send(message)
            except discord.errors.HTTPException:
                await self.channel.send(
                    "Confession quá dài. Hãy đảm bảo confession của bạn không quá 4000 kí tự."
                )

    async def send_private_confession(self):
        files = await self.send_files()

        content = f"``` Confession {server_info.confession_count}-ẩn danh```"
        embed = discord.Embed(
            title="**Tâm sự ẩn danh**",
            description=self.content,
            colour=discord.Colour.gold(),
        )
        embed.set_footer(text="""BetterMe - Better everyday""")
        await server_info.confession_channel.send(
            content=content, embed=embed, files=files
        )
        embed.add_field(name="**Id**", value=f"||{self.member.mention}||", inline=False)
        await server_info.manage_confession_channel.send(
            content=content, embed=embed, files=files
        )

    async def send_public_confession(self):
        files = await self.send_files()

        content = f"``` Confession {server_info.confession_count}-công khai```"
        embed = discord.Embed(
            title="**Tâm sự của " + self.member.name + "**",
            description=self.content,
            colour=discord.Colour.gold(),
        )
        embed.add_field(name="**Id**", value=f"||{self.member.mention}||", inline=False)
        embed.set_thumbnail(url=self.member.avatar or self.member.default_avatar.url)
        embed.set_footer(text="""BetterMe - Better everyday""")
        await server_info.confession_channel.send(
            content=content, embed=embed, files=files
        )
        await server_info.manage_confession_channel.send(
            content=content, embed=embed, files=files
        )


# end confession
@bot.tree.command(name="end_confession", description="Kết thúc confession")
async def end(interaction: discord.Interaction):
    await interaction.response.defer()
    confession = await Confessions.find_one(
        Confessions.channel_id == str(interaction.channel.id)
    )
    if confession:
        confession = Confession(
            channel=interaction.channel,
            member=await interaction.guild.fetch_member(confession.member_id),
            cfs_type=confession.type,
            files=[],
        )
        await confession.end_confession()
    else:
        await interaction.response(
            "Hãy gõ lệnh này trong kênh confession của bạn",
        )


@bot.listen()
async def on_interaction(interaction: discord.Interaction):
    if interaction.message:
        if (
            interaction.message.id == server_info.confession_dropdown_id
            and interaction.type == discord.InteractionType.component
        ):
            await interaction.response.defer()
            member = interaction.user
            values = interaction.data["values"]

            exist = await Confessions.find_one(Confessions.member_id == str(member.id))
            if exist:
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
                    cfs_type = "private"
                elif "public-confession" in values:
                    cfs_type = "public"

                confession = Confession(
                    channel=channel, member=member, cfs_type=cfs_type, files=[]
                )
                await confession.set_confession()
                await confession.end_confession()


async def fix_confession():
    now = datetime.datetime.now(datetime.timezone.utc)
    async for confession_data in Confessions.find():
        channel: discord.TextChannel
        member: discord.Member | discord.User
        channel, member = await asyncio.gather(
            *[
                server_info.guild.fetch_channel(int(confession_data.channel_id)),
                server_info.guild.fetch_member(int(confession_data.member_id)),
            ]
        )
        # delete if confession channel last longer than 40 minutes
        if (now - channel.created_at).seconds >= 2400:
            await Confession(
                channel=channel,
                member=member,
                cfs_type=confession_data.type,
                files=[],
            ).end_confession()
    print("fix confession done")
