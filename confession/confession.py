from base import (
    # necess
    discord,
    bot,
    tasks,
    View, Select,
    get,
    has_permissions, context, Interaction,
    # var
    guild_id,
    admin_id,
    confession_channel_id,
    private_confession_channel_id,
    confession_dropdown_id,
    confession_category_id
)

import asyncio
from typing import Optional, Union

from feature_func.mongodb import open_database, write_database
database_directory = "confession"

from .image_handle import save_image, delete_image
from .channel_name import channel_name


@bot.listen()
async def on_ready():
    global guild, confession_channel, private_confession_channel

    guild = bot.get_guild(guild_id)
    confession_channel = get(bot.get_all_channels(), id=confession_channel_id)
    private_confession_channel = get(bot.get_all_channels(),
                                     id=private_confession_channel_id)
    print('5.Confession ready')

class ConfessionOption(View):

    @discord.ui.select(
        placeholder="Lựa chọn",
        options=[
            discord.SelectOption(label= "Confession ẩn danh", value= 1, description= "Nơi bạn tâm sự những câu chuyện thầm kín"),
            discord.SelectOption(label= "Confession công khai", value= 2, description= "Nơi bạn tâm sự những câu chuyện thầm kín"),
        ]
    )
    async def select_callback(self, select, interaction):
        pass


@bot.command(name="confession")
@has_permissions(administrator=True)
async def kick(ctx: context.Context):
    view = ConfessionOption()
    await ctx.send(view=view)

##### confession process

class Confession():

    def __init__(self, cc_channel: discord.TextChannel, member: Optional[Union[discord.Member, discord.User]], cfs_type: str):
        self.cc_channel = cc_channel
        self.member = member
        self.cfs_type = cfs_type

        self.content = ""
        self.files = []

    async def set_confession(self):
        overwrite = discord.PermissionOverwrite()

        overwrite.view_channel = False
        everyone = get(self.member.guild.roles, id=guild_id)
        await self.cc_channel.set_permissions(everyone, overwrite=overwrite)
        overwrite.view_channel = True
        await self.cc_channel.set_permissions(self.member, overwrite=overwrite)

        embed = discord.Embed(
            title="**Nơi " + self.member.name + " tâm sự những câu chuyện thầm kín**",
            description=
            "Chúng mình luôn lắng nghe và chia sẻ mọi buồn vui cùng bạn",
            colour=discord.Colour.gold())
        embed.set_thumbnail(url=self.member.avatar.url)
        embed.add_field(
            name="**Chú ý**",
            value="Kênh sẽ biến mất sau 30 phút hoặc bạn gõ lệnh ``/end_confession`` ",
            inline=False)
        embed.set_footer(text='''BetterMe - Better everyday''')

        db = open_database(database_directory)
        db[str(self.cc_channel.id)] = {"user_id": self.member.id, "type": self.cfs_type}
        write_database(db, database_directory)
        await self.cc_channel.send(content=self.member.mention, embed=embed)

        await asyncio.sleep(1780)
        # await asyncio.sleep(20)
        db = open_database(database_directory)
        if str(self.cc_channel.id) in db.keys():
            await self.cc_channel.send(
                self.member.mention +
                "**Những lời tâm tư ngàn lời không nói hết. Nếu bạn muốn tiếp tục tâm sự hãy tạo 1 kênh mới. Kênh này sẽ biến mất sau 2 phút nữa. **"
            )
            await asyncio.sleep(120)
            # await asyncio.sleep(10)


    async def text_process(self):
        channel = get(bot.get_all_channels(), id=self.cc_channel.id)
        messages = [message async for message in channel.history(limit=200)]
        messages.reverse()
        for message in messages:
            if message.author.id == self.member.id:
                if message.content not in ["", "m,end", "M,end","/end_confession"]:
                    self.content += message.content + ". "
                if message.attachments:
                    for attach in message.attachments:
                        image = save_image(attach.url)
                        self.files.append(image)


    async def send_files(self):

        files_to_read: list[str] = self.files
        files_to_send: list[discord.File] = []

        for filename in files_to_read:
            with open(filename, 'rb') as f:
                files_to_send.append(discord.File(f))
            await delete_image(filename)
        return files_to_send


    async def end_confession(self):
        global guild
        channel_id = self.cc_channel.id

        db = open_database(database_directory)
        if str(channel_id) in db.keys():
            await self.text_process()

            if len(self.content) < 50 and self.files == []: 
                message = "Nội dung confession của bạn rất ngắn nên sẽ không được gửi đi. Lưu ý nếu gửi confession khó hiểu, không có chủ đích sẽ bị mute ít nhất 3 ngày"
            else:
                if self.cfs_type == "private":
                    await self.end_private_confession()
                elif self.cfs_type == "public":
                    await self.end_public_confession()
                db["confession_count"] = db["confession_count"] + 1
                message = "Cảm ơn bạn đã chia sẻ cùng chúng mình"
                
            await self.cc_channel.delete()
            del db[str(channel_id)]
            write_database(db, database_directory)
            await self.member.send(message)
                


    async def end_private_confession(self):
        global guild, confession_channel, private_confession_channel

        db = open_database(database_directory)
        files = await self.send_files()

        content = "``` Confession " + str(db["confession_count"]) + "-ẩn danh```"
        embed = discord.Embed(title="**Tâm sự ẩn danh**", description=self.content, colour=discord.Colour.gold())
        embed.set_footer(text='''BetterMe - Better everyday''')
        await private_confession_channel.send(content=content, embed=embed, files=files)
        embed.add_field(name="**Id**", value=f"||{self.member.mention}||", inline=False)
        await confession_channel.send(content=content, embed=embed, files=files)

    async def end_public_confession(self):
        global guild, confession_channel, private_confession_channel

        db = open_database(database_directory)
        files = await self.send_files()

        content = "``` Confession " + str(db["confession_count"]) + "-công khai```"
        embed = discord.Embed(title="**Tâm sự của " + self.member.name + "**", description=self.content, colour=discord.Colour.gold())
        embed.add_field(name="**Id**", value=f"||{self.member.mention}||", inline=False)
        embed.set_thumbnail(url=self.member.avatar.url)
        embed.set_footer(text='''BetterMe - Better everyday''')
        await private_confession_channel.send(content=content,embed=embed,files=files)
        await confession_channel.send(content=content, embed=embed, files=files)


# thực hiện lệnh
@bot.tree.command(name="end_confession", description="Kết thúc confession")
async def end(interaction: Interaction):
    await interaction.response.defer()
    db = open_database(database_directory)
    if str(interaction.channel.id) in db.keys():
        mem_id = db[str(interaction.channel.id)]["user_id"]
        cfs_type = db[str(interaction.channel.id)]["type"]

        member = bot.get_user(mem_id)
        confession = Confession(cc_channel=interaction.channel, member=member, cfs_type=cfs_type)
        await confession.end_confession()


@bot.listen()
async def on_interaction(interaction: Interaction):
    if interaction.message:
        if interaction.message.id == confession_dropdown_id and interaction.type == discord.InteractionType.component:
            
            db = open_database(database_directory)
            member = interaction.user
            values = interaction.data["values"]
            await interaction.response.defer()
            
            if str(member.id) in db.keys():
                await member.send("Bạn chỉ có thể tạo 1 kênh confession 1 lúc")
            elif "private-confession" in values or "public-confession" in values:
                member = interaction.user
                cc_name = channel_name(member.name, "confession")
                category = bot.get_channel(confession_category_id)
                cc_channel = await category.create_text_channel(cc_name,reason=None)

                #confession
                if "private-confession" in values:
                    cfs_type = "private"
                elif "public-confession" in values:
                    cfs_type = "public"
                
                confession = Confession(cc_channel=cc_channel, member= member, cfs_type=cfs_type)
                await confession.set_confession()
                await confession.end_confession()


async def fix_confession():
    pass
