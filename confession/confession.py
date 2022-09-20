import asyncio

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
async def set_confession(cc_channel, member, type: str):
    overwrite = discord.PermissionOverwrite()

    overwrite.view_channel = False
    everyone = get(member.guild.roles, id=guild_id)
    await cc_channel.set_permissions(everyone, overwrite=overwrite)
    overwrite.view_channel = True
    await cc_channel.set_permissions(member, overwrite=overwrite)

    embed = discord.Embed(
        title="**Nơi " + member.name + " tâm sự những câu chuyện thầm kín**",
        description=
        "Chúng mình luôn lắng nghe và chia sẻ mọi buồn vui cùng bạn",
        colour=discord.Colour.gold())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(
        name="**Chú ý**",
        value="Kênh sẽ biến mất sau 30 phút hoặc bạn gõ lệnh ``/end_confession`` ",
        inline=False)
    embed.set_footer(text='''BetterMe - Better everyday''')

    db = open_database(database_directory)
    db[str(cc_channel.id)] = {"user_id": member.id, "type": type}
    write_database(db, database_directory)
    await cc_channel.send(content=member.mention, embed=embed)

    await asyncio.sleep(1780)
    # await asyncio.sleep(20)
    if cc_channel:
        await cc_channel.send(
            member.mention +
            "**Những lời tâm tư ngàn lời không nói hết. Nếu bạn muốn tiếp tục tâm sự hãy tạo 1 kênh mới. Kênh này sẽ biến mất sau 2 phút nữa. **"
        )
        await asyncio.sleep(120)
        # await asyncio.sleep(10)


async def text_process(channel_id: int, mem_id: int):
    #test
    channel = get(bot.get_all_channels(), id=channel_id)
    messages = [message async for message in channel.history(limit=200)]
    for message in messages:
        if message.author.id == mem_id:
            db = open_database(database_directory)
            if message.content not in ["", "m,end", "M,end"]:
                db[str(message.author.id)]["content"] += message.content + ". "
            if message.attachments:
                for attach in message.attachments:
                    image = save_image(attach.url)
                    db = open_database(database_directory)
                    db[str(message.author.id)]["files"].append(image)
            write_database(db, database_directory)


async def send_files(file_list: list):
    files_to_read: list[str] = file_list
    files_to_send: list[discord.File] = []
    for filename in files_to_read:
        with open(filename, 'rb') as f:
            files_to_send.append(discord.File(f))
        await delete_image(filename)
    return files_to_send


async def end_confession(channel_id: int):
    global guild

    db = open_database(database_directory)
    if str(channel_id) in db.keys():
        mem_id = db[str(channel_id)]["user_id"]
        await text_process(channel_id, mem_id)
        mem_id = str(mem_id)
        db = open_database(database_directory)
        if len(db[mem_id]["content"]) < 50 and db[mem_id]["files"] == []:
            del db[mem_id]
            del db[str(channel_id)]
            write_database(db, database_directory)
            cc_channel = get(bot.get_all_channels(), id=channel_id)
            await cc_channel.delete()
            member = bot.get_user(int(mem_id))
            await member.send("Nội dung confession của bạn rất ngắn nên sẽ không được gửi đi. Lưu ý nếu gửi confession khó hiểu, không có chủ đích sẽ bị mute ít nhất 3 ngày.")

        elif db[str(channel_id)]["type"] == "private":
            await end_private_confession(channel_id, mem_id)
        elif db[str(channel_id)]["type"] == "public":
            await end_public_confession(channel_id, mem_id)


async def end_private_confession(channel_id: int, mem_id: str):
    global guild, confession_channel, private_confession_channel

    member = await bot.fetch_user(int(mem_id))
    db = open_database(database_directory)

    content = "``` Confession " + str(db["confession_count"]) + "-ẩn danh```"
    embed = discord.Embed(title="**Tâm sự ẩn danh**",
                          description=db[str(mem_id)]["content"],
                          colour=discord.Colour.gold())
    files = await send_files(db[str(mem_id)]["files"])
    embed.set_footer(text='''BetterMe - Better everyday''')
    await private_confession_channel.send(content=content, embed=embed, files=files)
    embed.add_field(name="**Id**", value="||<@" + mem_id + ">||", inline=False)
    await confession_channel.send(content=content, embed=embed, files=files)

    db = open_database(database_directory)
    db["confession_count"] = db["confession_count"] + 1
    del db[mem_id]
    del db[str(channel_id)]
    write_database(db, database_directory)

    cc_channel = get(bot.get_all_channels(), id=channel_id)
    await cc_channel.delete()
    await member.send("Cảm ơn bạn đã chia sẻ cùng chúng mình")


async def end_public_confession(channel_id: int, mem_id: str):
    global guild, confession_channel, private_confession_channel

    member = await bot.fetch_user(int(mem_id))
    db = open_database(database_directory)
    files = await send_files(db[str(mem_id)]["files"])

    content = "``` Confession " + str(db["confession_count"]) + "-công khai```"
    embed = discord.Embed(title="**Tâm sự của " + member.name + "**",
                          description=db[str(mem_id)]["content"],
                          colour=discord.Colour.gold())
    embed.add_field(name="**Id**", value="||<@" + mem_id + ">||", inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text='''BetterMe - Better everyday''')
    await private_confession_channel.send(content=content,
                                        embed=embed,
                                        files=files)
    await confession_channel.send(content=content, embed=embed, files=files)

    db = open_database(database_directory)
    db["confession_count"] = db["confession_count"] + 1
    del db[mem_id]
    del db[str(channel_id)]
    write_database(db, database_directory)

    cc_channel = get(bot.get_all_channels(), id=channel_id)
    await cc_channel.delete()
    await member.send("Cảm ơn bạn đã chia sẻ cùng chúng mình")


# thực hiện lệnh
@bot.tree.command(name="end_confession", description="Kết thúc confession")
async def end(interaction: Interaction):
    await interaction.response.defer()
    await end_confession(interaction.channel.id)


@bot.listen()
async def on_interaction(interaction: Interaction):
    if interaction.message.id == confession_dropdown_id and interaction.type == discord.InteractionType.component:
        
        db = open_database(database_directory)
        member = interaction.user
        values = interaction.data["values"]
        await interaction.response.defer()
        if str(member.id) in db.keys():
            await member.send("Bạn chỉ có thể tạo 1 kênh confession 1 lúc")
        elif "private-confession" in values or "public-confession" in values:
            db[str(member.id)] = {"content": "", "files": []}
            member = interaction.user
            cc_name = channel_name(member.name, "confession")
            category = bot.get_channel(confession_category_id)
            cc_channel = await category.create_text_channel(cc_name,reason=None)

            #confession
            write_database(db, database_directory)
            if "private-confession" in values:
                await set_confession(cc_channel, member, "private")
            elif "public-confession" in values:
                await set_confession(cc_channel, member, "public")

            db = open_database(database_directory)
            if str(member.id) in db.keys():
                await end_confession(cc_channel.id)
            else:
                print("not found " + member.name)
