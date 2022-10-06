from base import (
  # necess
  discord, bot, tasks, 
  get, has_role, Interaction, app_commands,
  # var
  diary_channel_id, admin_role_id
)

from datetime import datetime, timedelta
from typing import Optional, Union

from feature_func.mongodb import open_database, write_database

exact_bad_words = [
'lồn', 'conmemay', 'đĩ', 'cứt', 'cức', 'đụ', 'cuming', 'cock', 'đù', 'vl', 'lìn', 'mf', 'cmn'
]

included_bad_words = [
'dkm', 'cặc', 'cặk', 'cẹc', 'bitch', 'địt', 'loz', 'đjt', 'djt', 'buồi', 'buoi`', "buoi'", 'đm', 'vcl', 'đéo', 'đ!t', 'd!t', 'clm', 'cđm', 'vkl', 'vklm', 'vcc', 'vcđ', 'vcd',  'đcm', 'dcm'
'pussy', 'blowjob', 'titjob', 'wtf', 'fuck', 'fuk',
]

space_bad_words = []

def check_bad_words(content: str) -> bool:
    global exact_bad_words, included_bad_words

    content = content.lower()
    content_words = content.split(" ")

    for word in content_words:

        # check exact
        if word in exact_bad_words:
            return False

        # check included
        if word.startswith("http") or word.startswith(":"):
            pass
        else:
            for bad_word in included_bad_words:
                if bad_word in word:
                    return False
    
    return True

def punish(mem_id: int, message_content: str):
    value = open_database("bad_words")
    
    mem_id = str(mem_id)
    if mem_id not in value:
        value[mem_id] = {
            'bad_word_list': [
                (discord.utils.utcnow(), message_content)
            ],
        }
    else:
        value[mem_id]['bad_word_list'].append((discord.utils.utcnow(), message_content))

    counter = len(value[mem_id]['bad_word_list'])
    write_database(value, "bad_words")

    if counter < 3:
        form = 'WARN'
        hours = 0
        penalize = "Cảnh báo"
        colour = discord.Colour.orange()
    else:
        colour = discord.Colour.red()
        if counter <= 8:
            if counter == 3:
                hours = 3
            elif counter == 4:
                hours = 12
            elif counter == 5:
                hours = 24
            elif counter == 6:
                hours = 72
            elif counter == 7:
                hours = 180
            elif counter == 8:
                hours = 360

            form = 'MUTE'
            penalize = f"Thời gian chờ {hours} tiếng"

        elif counter >= 9:
            form = 'BAN'
            hours = 0
            penalize = f"BAN !!!"

    return (form, hours, penalize, colour)

### Các mức phạt:
# 1-2 lần: warn
# 3 lần: tempmute 3h
# 4 lần: tempmute 12h
# 5 lần: tempmute 24h
# 6 lần: tempmute 72h
# 7 lần: tempmute 360h
# 8 lần: ban

# Sau 30 ngày thì những tội 30 ngày trước đó sẽ được xóa bỏ


diary_channel = None
muted_role = None

@bot.listen()
async def on_ready():
    global diary_channel

    diary_channel = get(bot.get_all_channels(), id = diary_channel_id)
    # diary_channel = get(bot.get_all_channels(), id = 884447828330549349)


@bot.listen()
async def on_message(message: discord.Message):
    global diary_channel

    if check_bad_words(message.content) == False:
        print(message.content)

        try:
            await message.delete()
        except discord.errors.NotFound:
            print("Not found message")

        # xu ly
        form, hours, penalize, colour = punish(message.author.id, message.content)
        reason = "Ngôn từ không phù hợp"
        if form == 'WARN':
            pass
        elif form == 'MUTE':
            unmuted_time = discord.utils.utcnow() + timedelta(hours= hours)
            await message.author.timeout(unmuted_time, reason= reason)
        elif form == 'BAN':
            await message.author.ban(reason= reason)
        
        # send to channel
        embed = discord.Embed(
            title= None,
            description=f"**Lý do:** {reason}",
            colour= colour
        )
        embed.set_author(name =  f"[{form}] {message.author.name}#{message.author.discriminator}", icon_url = message.author.avatar.url)
        await message.channel.send(content= message.author.mention, embed= embed)

        # send to diary
        embed = discord.Embed(colour = colour)
        embed.set_author(name =  f"[{form}] {message.author.name}#{message.author.discriminator}", icon_url = message.author.avatar.url)
        embed.add_field(name= "User", value= message.author.mention, inline= True)
        embed.add_field(name= "Moderator", value= bot.user.mention, inline= True)
        embed.add_field(name= "Reason", value= reason, inline= True)
        embed.add_field(name= "Channel", value= f"<#{message.channel.id}>", inline= False)
        embed.add_field(name= "Message", value= message.content, inline= False)
        embed.add_field(name= "Penalize", value= penalize, inline= False)

        await diary_channel.send(embed= embed)


@bot.tree.command(name= "timeout", description= "Xử phạt người dùng")
@has_role(admin_role_id)
@app_commands.describe(member="Người bị xử phạt")
@app_commands.describe(hours="Thời gian xử phạt(giờ)")
@app_commands.describe(reason="Lý do")
async def timeout(interaction: Interaction, member: discord.Member, hours: int, reason: Optional[str]):

    unmuted_time = discord.utils.utcnow() + timedelta(hours= hours)
    await member.timeout(unmuted_time, reason= reason)
    await interaction.response.send_message(f"Đã cài thời gian chờ cho {member.mention} trong {hours} giờ tiếp theo.\n**Lý do:**{reason}")
