#### main
import os
import discord
from easy_mongodb import db
import time
import asyncio
from discord.utils import get
from discord.ext import commands
from waiting import wait
from dotenv import load_dotenv

from discord_slash import SlashCommand,SlashContext
from discord_slash.utils.manage_commands import create_option

#voice channel name
def channel_name(name):
  global name_check

  kq = "-"
  for i in range(len(name)):
    #print(str(i)+" "+name[i])
    if name[i] in name_check:
      kq = kq + name[i].lower()
    elif name[i] == " " and name[i-1] !=" " and kq[len(kq)-1] != "-":
        kq = kq + "-"

  #print("kq1:"+kq)

  if kq == "" or kq == "-":
    kq = xuly_cn()
  
  else:
    #xử lý tên sau khi lấy
    while kq[len(kq)-1]=="-":
      if kq == "" or kq == "-":
        kq = xuly_cn()
      else:
        kq = kq[:-1:]
    
    i=0
    while kq[i] == "-":
      kq=kq[1::]   

  print(kq)
  return kq

def xuly_cn():
  kq = ""
  i = 1
  while str(i) in db["name"]:
    i = i+1
  kq = str(i) 
  db["name"][str(i)] = i
  return kq


#check avaiable name
ban_word =[
  "đụ","địt","đ ụ","đjt","djt",
  "đm","đmm","cđm","vc","d!t","vkl","vcc","vklm","sml","vclm"
  "loz","lồn","l o z",
  "cẹc","buồi","buoi'","cặc","cặk",
  "đĩ","điếm",
  "cock","dick","pussy","porn","bitch","fuk",
  "đéo",
]

def check_avaiable_name(content):
  msg = content.lower()
  #msg = " ".join(msg.split())
  msg = msg.replace(" ", "")
  #print(msg)
  check = any(ele in msg for ele in ban_word)
  if check == False:
    return True
  else:
    return False



intents = discord.Intents().all()
client = commands.Bot(command_prefix=["m,","M,"] , intents = intents)
slash = SlashCommand(client, sync_commands=True)

guild = client.get_guild(880360143768924210)
guild_ids = [880360143768924210]
everyone_id = 880360143768924210

#default_data
vc_value = {
  "cc_id":0,
  "host_id":0,
  "channel_name":""
}
cc_value = {
  "vc_id":0,
  "host_id":0,
  "pos":""
}
user_value={
  "id":0,
  "vc_id":0,
  "cc_id":0,
  "locate":""
}

#db["name"]={"0":0,}
#db["pos"]={"0":0,}

name_check=["q","w","e","r","t","y","u","i","o","p",
"a","s","d","f","g","h","j","k","l",
"z","x","c","v","b","n","m",

"Q","W","E","R","T","Y","U","I","O","P",
"A","S","D","F","G","H","J","K","L",
"Z","X","C","V","B","N","M",

"0","1","2","3","4","5","6","7","8","9",

"ă","â","đ","ê","ô","ơ","ư",
"á","à","ã","ả","ạ",
"ắ","ằ","ặ","ẵ","ẳ",
"ầ","ấ","ẩ","ẫ","ậ",
"è","ẻ","é","ẽ","ẹ",
"ề","ế","ể","ễ","ệ",
"ồ","ố","ổ","ỗ","ộ",
"ờ","ớ","ở","ỡ","ợ",
"ừ","ứ","ử","ữ","ự",
"í","ì","ĩ","ỉ","ị",
"ỳ","ý","ỵ","ỷ","ỹ",
"ò","ó","õ","ỏ","ọ",
"ù","ú","ũ","ụ","ủ",

"_"]

number = [
"0","1","2","3","4","5","6","7","8","9",
]

command_mess="""
**Các lệnh:**
```
/public: mở phòng cho tất cả mọi người vào

/private: khóa phòng, chỉ những người được mời mới vào được

/allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

/invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

/disallow | /kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

/limit + [số_người_giới_hạn]

/rename + [tên phòng]: đổi tên phòng

```

***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ những người đang trong phòng của bạn mới thấy
-Phòng sẽ mất khi không còn ai trong phòng
-Bạn có thể gọi bot trong kênh này
||Chúc các bạn học vui =)))||
"""

command_mess_ts="""
**Các lệnh:**
```
/public: mở phòng cho tất cả mọi người vào

/private: khóa phòng, chỉ những người được mời mới vào được

/hide: ẩn phòng với mọi người

/show: hiện phòng với mọi người

/allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

/invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

/disallow | /kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

/limit + [số_người_giới_hạn]

/rename + [tên phòng]: đổi tên phòng

```

***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ những người đang trong phòng của bạn mới thấy
-Phòng sẽ mất khi không còn ai trong phòng
-Bạn có thể gọi bot trong kênh này
||Có gì khúc mắc hãy tâm sự cùng mọi người nhé||
"""



command_mess_sg="""
**Các lệnh:**
```
/public: mở phòng cho tất cả mọi người vào

/private: khóa phòng, chỉ những người được mời mới vào được

/allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

/invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

/disallow | /kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

/limit + [số_người_giới_hạn]

/rename + [tên phòng]: đổi tên phòng

```

***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ những người đang trong phòng của bạn mới thấy
-Phòng sẽ mất khi không còn ai trong phòng
||Chúc các bạn học vui =)))||
"""


command_mess_cp="""
**Các lệnh:**
```
/public: mở phòng cho tất cả mọi người vào

/private: khóa phòng, chỉ những người được mời mới vào được

/hide: ẩn phòng với mọi người

/show: hiện phòng với mọi người

/allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

/invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

/disallow | /kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

/rename + [tên phòng]: đổi tên phòng

```

***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ những người đang trong phòng của bạn mới thấy
-Phòng sẽ mất khi không còn ai trong phòng
||Chúc các bạn phát cơm tró vui vẻ =)))||
"""
command_mess_sa="""
**Các lệnh:**
```
/rename + [tên phòng]: đổi tên phòng
```
***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ 1 mình bạn thấy
-Phòng sẽ mất khi không còn ai trong phòng
||Chúc bạn tự kỉ vui vẻ =)))||
"""

channel_cre=[
  918549426732142653,918549341948497961,918549182107746356,922461169799790642,923964509935243265
]

full_cam_id =[
915238716803514389,
915923719216574485
]
cam_stream_id = [
947404118979403796,
947404163103465512
]



#----------START-----------

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(' ')

@client.event
async def on_member_join(member):

  embed= discord.Embed(
  title = "**Chào mừng "+member.name+" đến với Cộng Đồng học tập BetterMe**",
  description =" Hãy giới thiệu bản thân cho mọi người biết ở <#894594032947310602> nhé",
  colour = discord.Colour.gold()
  )

  welcome_channel = get(member.guild.channels, id=894594032947310602)

  pfp = member.avatar_url
  field1="Hãy đọc kĩ luật ở <#880369537449619476> nha"
  field2="Nếu bạn chưa biết cách dùng Discord thì ở <#915949063403347968> có đó"
  field3="Hãy vào <#891909866355048548> để nhận role tương ứng nha"

  embed.set_footer(text='''Chúc bạn có 1 khoảng thời gian vui vẻ. 
BetterMe-Better everyday''')
  embed.set_image(url="https://i.ibb.co/Wvw2CY9/Betterme.png")
  embed.set_thumbnail(url=pfp)
  embed.add_field(name="**Đọc kĩ luật**",value=field1,inline=False)
  embed.add_field(name="**Hướng dẫn cơ bản**",value=field2,inline=False)
  embed.add_field(name="**Set role**",value=field3,inline=False)
	
  msg = await welcome_channel.send(content=member.mention,embed=embed)
  await asyncio.sleep(660)
  await msg.delete()

can_clear = True
can_create = True

@client.event
async def on_voice_state_update(member, member_before, member_after):
  global can_clear,can_create

##################### create-voice-channel #####################
  voice_channel_before = member_before.channel
  voice_channel_after = member_after.channel
  #print("-------"+str(member)+"----------")
  #print(voice_channel_before)
  #print(voice_channel_after)

  mem_id = str(member.id)
  mem_name = str(member.name)

# thứ tự: mem out -> cre -> edit channel -> mem in

##create channel + set role
  if voice_channel_after != None:
    if voice_channel_after.id in channel_cre:
      can_clear = False
      if mem_id not in db.keys():
        if check_avaiable_name(member.name) == False:
          await member.move_to(None)
          await member.send("**Bạn hãy kiểm tra và đảm bảo trong tên của bạn không có từ cấm, tục tĩu**")
        else:
          try:
            #set channel
            db[mem_id] = None
            db[mem_id] = {}
            if voice_channel_after.id == 918549426732142653:
              category=client.get_channel(900439704950956053)
              db[mem_id]["locate"]="sg"
              lim = 15

            elif voice_channel_after.id == 918549341948497961:
              category=client.get_channel(901518444271386694)
              db[mem_id]["locate"]="cp"
              lim = 2

            elif voice_channel_after.id == 918549182107746356:
              category=client.get_channel(900598666572750929)
              db[mem_id]["locate"]="sa"
              lim = 1

            elif voice_channel_after.id == 922461169799790642:
              category=client.get_channel(915512539733975050)
              db[mem_id]["locate"]="cr"
              lim = 0
            elif voice_channel_after.id == 923964509935243265:
              category=client.get_channel(902499044356657173)
              db[mem_id]["locate"]="ts"
              lim = 0


            #create
            cc_name = channel_name(mem_name)
            vc_name = "#"+cc_name + "'s room"
            vc_channel = await category.create_voice_channel(vc_name,overwrites=None, reason=None)
            #database_1
            vcid = vc_channel.id
            uid = member.id
            db[str(vcid)] = {
                "cc_id":0,
                "host_id":uid,
                "channel_name":vc_name
              }

            if member in voice_channel_after.members:
              await member.move_to(vc_channel)
              cc_channel = await category.create_text_channel(cc_name,overwrites=None, reason=None)

              #database_2
              ccid = cc_channel.id

              db[str(ccid)] = {
                "vc_id":vcid,
                "host_id":uid,
              }

              db[mem_id]["vc_id"] = vcid
              db[mem_id]["cc_id"] = ccid
              db[mem_id]["id"] = uid

              db[str(vcid)]["cc_id"] = ccid

              #####set permission
              #everyone
              overwrite = discord.PermissionOverwrite()
              
              overwrite.view_channel=False
              overwrite.connect=False
              #overwrite.manage_channels=False
              #overwrite.manage_permissions=False
              overwrite.move_members=False
              role = get(member.guild.roles, id=880360143768924210)
              await cc_channel.set_permissions(role, overwrite=overwrite)
              overwrite.view_channel=True   
              #print(vc_channel.name,vc_channel.id)
              await vc_channel.set_permissions(role, overwrite=overwrite)
              #user
              overwrite.view_channel=True
              overwrite.connect=True
              overwrite.move_members=True
              overwrite.send_messages=True
              overwrite.embed_links=True
              overwrite.attach_files=True
              overwrite.read_message_history=True
              overwrite.use_external_emojis=True
              overwrite.add_reactions=True
              await cc_channel.set_permissions(member, overwrite=overwrite)
              ###overwrite.manage_channels=True
              ###overwrite.manage_permissions=True
              await vc_channel.set_permissions(member, overwrite=overwrite)
              #bot
              role = get(member.guild.roles, id=887181406898376704)
              overwrite.send_messages=True
              await cc_channel.set_permissions(role, overwrite=overwrite)
              await vc_channel.set_permissions(role, overwrite=overwrite)
              await vc_channel.edit(user_limit= lim)

              #hướng dẫn
              if db[mem_id]["locate"]=="cp":
                await cc_channel.send("<@"+mem_id+">"+command_mess_cp)
              elif db[mem_id]["locate"]=="sa":
                await cc_channel.send("<@"+mem_id+">"+command_mess_sa)
              elif db[mem_id]["locate"]=="sg":
                await cc_channel.send("<@"+mem_id+">"+command_mess_sg)
              elif db[mem_id]["locate"]=="ts":
                await cc_channel.send("<@"+mem_id+">"+command_mess_ts)
              else:
                await cc_channel.send("<@"+mem_id+">"+command_mess)
            else:
              await vc_channel.delete()
              del db[mem_id]
              del db[str(vcid)]

          except Exception as e:
            print(e)
            try:
              del db[mem_id]
            except:
              print("can delete mem id")

            try:
              del db[str(vcid)]
            except:
              print("can delete vc id")

            try:
              del db[str(ccid)]
            except:
              print("can delete cc id")

      else: 
              await member.move_to(None)
              await member.send("Bạn chỉ có thể tạo 1 phòng cùng lúc")  
      can_clear = True




##member out
  if voice_channel_after != voice_channel_before and voice_channel_before != None:
    if str(voice_channel_before.id) in db.keys():
      can_clear = False

      vc = str(voice_channel_before.id) 

      if db[str(voice_channel_before.id)]["host_id"] != member.id: 
        if mem_id in db.keys():
          del db[mem_id]
      #role_names = [role.name for role in member.roles]
      #if "FEATURE BOT" in role_names:
        #pass 
      if voice_channel_before.members == []:

        if vc in db.keys():
          text_channel = db[vc]["cc_id"]

          channel_del = client.get_channel(int(vc))
          if channel_del != None:
            await channel_del.delete()          
          channel_del = client.get_channel(text_channel)
          if channel_del != None:
            await channel_del.delete() 
          
          clone_channel = db[vc]["channel_name"]
          if clone_channel in db["name"]:
            del db["name"][clone_channel]

          if str(db[vc]["cc_id"]) in db.keys():
            del db[str(db[vc]["cc_id"])]
          if str(db[vc]["host_id"]) in db.keys():
            del db[str(db[vc]["host_id"])]
          del db[vc]    

      else:  
        cc_channel = get(client.get_all_channels(), id=db[vc]["cc_id"] )
        
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel=False
        overwrite.send_messages=False
        overwrite.embed_links=False
        overwrite.attach_files=False
        overwrite.read_message_history=False
        overwrite.use_external_emojis=False
        overwrite.add_reactions=False
        
        await cc_channel.set_permissions(member, overwrite=overwrite)
        #await cc_channel.remove_permissions(member)

      can_clear = True

##member in    
  elif voice_channel_after != voice_channel_before and voice_channel_after != None:
    if str(voice_channel_after.id) in db.keys():
          can_clear = False
          cc_channel = get(client.get_all_channels(), id=db[str(voice_channel_after.id)]["cc_id"] )
          if cc_channel != None:
            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel=True
            overwrite.send_messages=True
            overwrite.embed_links=True
            overwrite.attach_files=True
            overwrite.read_message_history=True
            overwrite.use_external_emojis=True
            overwrite.add_reactions=True
            await cc_channel.set_permissions(member, overwrite=overwrite)
  
            category_id = voice_channel_after.category.id
            if category_id == 900439704950956053:
              locate ="sg"
            elif category_id == 901518444271386694:
              locate ="cp"
            elif category_id == 900598666572750929:
              locate ="sa"
            elif category_id == 915512539733975050:
              locate ="cr"
            elif category_id == 902499044356657173:
              locate ="ts"
  
            #print(locate)
            if mem_id not in db.keys():
              db[mem_id]={
                "vc_id":voice_channel_after.id,
                "locate":locate
              }
          can_clear = True

	
#################check cam bot################################

  if member_after.channel != None:
  ###############only cam      
  ####check cam on
      if member_after.channel.id in full_cam_id:
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False:
            print("kick cam start")
            await asyncio.sleep(10)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and mem_voice_state.channel.id in full_cam_id:

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng FULL CAM. Hãy bật camera, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')

                msg = await member.send(content=member.mention,embed=embed)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and mem_voice_state.channel.id in full_cam_id:
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')
                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick cam end")



  ###############cam | stream
  ####check cam on
      if member_after.channel.id in cam_stream_id:
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False and mem_voice_state.self_stream == False:
            print("kick stream start")
            await asyncio.sleep(10)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and mem_voice_state.channel.id in cam_stream_id:

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng CAM/STREAM. Hãy bật camera hoặc stream, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')

                msg = await member.send(content=member.mention,embed=embed)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and mem_voice_state.channel.id in cam_stream_id:
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam hoặc stream",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam/stream",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick stream end")

#################custom check cam bot################################
  ###############custom only cam      
  ####check cam on
      if member_after.channel.name.lower().startswith("full cam") :
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False:
            print("kick cam start")
            await asyncio.sleep(15)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and member_after.channel.name.lower().startswith("full cam"):

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng FULL CAM. Hãy bật camera, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')

                msg = await member.send(content=member.mention,embed=embed)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and member_after.channel.name.lower().startswith("full cam"):
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')
                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick cam end")



  ###############custom cam | stream
  ####check cam on
      if member_after.channel.name.lower().startswith("cam stream"):
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False and member_after.channel.name.lower().startswith("cam stream"):
            print("kick stream start")
            await asyncio.sleep(15)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and member_after.channel.name.lower().startswith("cam stream"):

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng CAM/STREAM. Hãy bật camera hoặc stream, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')

                msg = await member.send(content=member.mention,embed=embed)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and member_after.channel.name.lower().startswith("cam stream"):
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam hoặc stream",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam/stream",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick stream end")
	
	
	
	
#####################################command

@client.command(name="clean", description="room clear")
async def clean(ctx):
  print("clear")
  global can_clear, can_create
  if can_clear == False or ctx.channel.id != 884447828330549349:
    await ctx.send("Không thể clear lúc này. Vui lòng thử lại sau")
  else:
    async with ctx.typing():
      can_create = False

      client.loop.create_task(fix_before_start())

      can_create = True
    await ctx.send("fix done")
	




######################################slash command
#id
@slash.slash(
  name="Id",
  description="Lấy id",
  guild_ids=guild_ids,
  options =[
    create_option(
      name="member",
      description="Người bạn muốn mời",
      required=True,
      option_type=6)

  ]
  )
async def _hello(ctx:SlashContext,member:str):
  await ctx.send(str(member.id))


#################################public
@slash.slash(
  name="public",
  description="Cho phép vào phòng",
  guild_ids=guild_ids,
  )
async def _public(ctx:SlashContext):
  if str(ctx.author.id) in db.keys():
    vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] )      
    overwrite = discord.PermissionOverwrite()
    overwrite.connect=True
    role = get(ctx.guild.roles, id=everyone_id)
    await vc_channel.set_permissions(role, overwrite=overwrite)
    await ctx.send("Phòng đã được mở cho mọi người vào") 

#################################private
@slash.slash(
  name="private",
  description="Không phép vào phòng",
  guild_ids=guild_ids,
  )
async def _private(ctx:SlashContext):
  if str(ctx.author.id) in db.keys():
    vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] )      
    overwrite = discord.PermissionOverwrite()
    overwrite.connect=False
    role = get(ctx.guild.roles, id=everyone_id)
    await vc_channel.set_permissions(role, overwrite=overwrite)
    await ctx.send("Phòng đã được đóng không cho mọi người vào") 

#################################show
@slash.slash(
  name="show",
  description="Hiện phòng cho mọi người thấy",
  guild_ids=guild_ids,
  )
async def _show(ctx:SlashContext):
  if str(ctx.author.id) in db.keys():
    check = db[str(ctx.author.id)]["locate"]
    if check == "ts" or check == "cp":
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] )     
      overwrite = discord.PermissionOverwrite()
      overwrite.view_channel=True
      overwrite.connect=False
      role = get(ctx.guild.roles, id=everyone_id)
      await vc_channel.set_permissions(role, overwrite=overwrite)
      await ctx.send("Phòng đã được hiện cho mọi người thấy")

#################################hide
@slash.slash(
  name="hide",
  description="Ẩn phòng không cho mọi người thấy",
  guild_ids=guild_ids,
  )
async def _hide(ctx:SlashContext):
  if str(ctx.author.id) in db.keys():
    check = db[str(ctx.author.id)]["locate"]
    if check == "ts" or check == "cp":
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] )     
      overwrite = discord.PermissionOverwrite()
      overwrite.view_channel=False
      role = get(ctx.guild.roles, id=everyone_id)
      await vc_channel.set_permissions(role, overwrite=overwrite)
      await ctx.send("Phòng đã ẩn không cho mọi người thấy")

#################################limit
@slash.slash(
  name="limit",
  description="Đặt giới hạn phòng",
  guild_ids=guild_ids,
  options =[
  create_option(
    name="limit",
    description="Đặt limit cho phòng",
    required=True,
    option_type=4
    )
  ]
  )
async def _limit(ctx:SlashContext,limit:int):
  if str(ctx.author.id) in db.keys():
    check = db[str(ctx.author.id)]["locate"]
    lim = limit
    if check == "cr" or check == "ts":
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] )  
      if lim <= 0: await ctx.send("Bạn không thể đặt limit phòng là 0 hoặc bé hơn")
      elif lim >25:
        if lim <99:
          await vc_channel.edit(user_limit= lim)
          await ctx.send("Bạn đã đặt limit phòng: "+str(lim))
        else:
          await vc_channel.edit(user_limit=0)
          await ctx.send("Bạn đã đặt limit phòng: Vô hạn")
        await ctx.send("Với những phòng lim>25, bạn sẽ không thể bật được CAM")
      else:
        await vc_channel.edit(user_limit = lim)
        await ctx.send("Bạn đã đặt limit phòng: "+str(lim))
    elif check == "sg":
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] )  
      if lim <= 0: await ctx.send("Bạn không thể đặt limit phòng là 0 hoặc bé hơn")
      elif lim >=1 and lim <=15:
        await vc_channel.edit(user_limit= lim)
        await ctx.send("Bạn đã đặt limit phòng: "+str(lim))
      else:
        await ctx.send("Bạn không thể đặt limit phòng Small Group lớn hơn 15 ")
    elif check == "cp":
      await ctx.send("Bạn không thể đặt limit cho phòng Couple")
    elif check == "sa":
      await ctx.send("Bạn không thể đặt limit cho phòng Study Alone")


#################################invite member
@slash.slash(
  name="invite",
  description="Mời bạn vào phòng",
  guild_ids=guild_ids,
  options =[
    create_option(
      name="member",
      description="Người bạn muốn mời",
      required=True,
      option_type=6
      )
  ]
  )
async def _invite(ctx:SlashContext,member:str):
  if str(ctx.author.id) in db.keys():
    if member:
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] ) 
      overwrite = discord.PermissionOverwrite()
      overwrite.view_channel=True
      overwrite.connect=True
      await vc_channel.set_permissions(member, overwrite=overwrite) 
      invite_link = await vc_channel.create_invite(max_uses=1,unique=True)
      await member.send("**"+str(ctx.author.name)+"** đã mời bạn vào học: "+str(invite_link))
      await ctx.send("Đã mời <@"+str(member.id)+"> vào phòng")
    else :
      await ctx.send("Không tìm thấy người dùng")  

#############################allow member
@slash.slash(
  name="allow",
  description="Cho phép vào phòng",
  guild_ids=guild_ids,
  options =[
    create_option(
      name="member",
      description="Người bạn cho phép",
      required=True,
      option_type=6
      )
  ]
  )
async def _allow(ctx:SlashContext,member:str):
  if str(ctx.author.id) in db.keys():
    if member:
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] ) 
      overwrite = discord.PermissionOverwrite()
      overwrite.view_channel=True
      overwrite.connect=True
      await vc_channel.set_permissions(member, overwrite=overwrite) 
      await ctx.send("Đã cấp quyền cho <@"+str(member.id)+"> vào phòng")
    else :
      await ctx.send("Không tìm thấy người dùng")

#############################disallow|kick member
@slash.slash(
  name="disallow",
  description="Không phép vào phòng",
  guild_ids=guild_ids,
  options =[
    create_option(
      name="member",
      description="Người bạn không cho phép",
      required=True,
      option_type=6
      )
  ]
  )
async def _disallow(ctx:SlashContext,member:str):
  if str(ctx.author.id) in db.keys():
    if member:
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] ) 
      if member in vc_channel.members and db[str(vc_channel.id)]["host_id"] != member.id:
        overwrite = discord.PermissionOverwrite()
        overwrite.connect=False
        await vc_channel.set_permissions(member, overwrite=overwrite) 
        await member.move_to(None)
        await ctx.send("<@"+str(member.id)+"> đã mất quyền vào phòng")
      elif db[str(vc_channel.id)]["host_id"] != member.id:
        overwrite = discord.PermissionOverwrite()
        overwrite.connect=False
        await vc_channel.set_permissions(member, overwrite=overwrite) 
        await ctx.send("<@"+str(member.id)+"> đã mất quyền vào phòng")
      else: 
        await ctx.send("Bạn không thể kick chủ phòng")

#############################disallow|kick member
@slash.slash(
  name="kick",
  description="Kick khỏi phòng",
  guild_ids=guild_ids,
  options =[
    create_option(
      name="member",
      description="Người bạn không cho phép",
      required=True,
      option_type=6
      )
  ]
  )
async def _kick(ctx:SlashContext,member:str):
  if str(ctx.author.id) in db.keys():
    if member:
      vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] ) 
      if member in vc_channel.members and db[str(vc_channel.id)]["host_id"] != member.id:
        overwrite = discord.PermissionOverwrite()
        overwrite.connect=False
        await vc_channel.set_permissions(member, overwrite=overwrite) 
        await member.move_to(None)
        await ctx.send("<@"+str(member.id)+"> đã mất quyền vào phòng")
      elif db[str(vc_channel.id)]["host_id"] != member.id:
        overwrite = discord.PermissionOverwrite()
        overwrite.connect=False
        await vc_channel.set_permissions(member, overwrite=overwrite) 
        await ctx.send("<@"+str(member.id)+"> đã mất quyền vào phòng")
      else: 
        await ctx.send("Bạn không thể kick chủ phòng")

##############rename channel
@slash.slash(
  name="rename",
  description="Đổi tên phòng",
  guild_ids=guild_ids,
  options =[
  create_option(
    name="text",
    description="Tên phòng",
    required=True,
    option_type=3
    )
  ]
)
async def _rename(ctx:SlashContext,text:str):
  if str(ctx.author.id) in db.keys():
    if check_avaiable_name(text) == True:
      new_name = text
      if len(new_name) > 50:
        await ctx.send("Tên quá dài")
      else:  
        vc_channel = get(client.get_all_channels(), id=db[str(ctx.author.id)]["vc_id"] ) 
        await vc_channel.edit(name=new_name)
        await ctx.send("Tên kênh đã được đổi thành "+new_name)
    else:
      await ctx.send("**Không được đổi tên kênh có những từ cấm nha mầy, tau táng cho á**")

@client.event
async def on_message(message):
  global i,store,new_mem
  if message.author == client.user:
    return

  if str(message.channel)== "giới-thiệu-bản-thân" and len(message.content) <120 :
    await message.delete()
    embed= discord.Embed(
    title = "**Chào mừng "+message.author.name+" đến với Cộng Đồng học tập BetterMe**",
    description ="Bạn giới thiệu đầy đủ 1 xíu nha.",
    colour = discord.Colour.gold()
    )
    coban = '''
Tên tuổi
Năm sinh
Nơi ở
Sở thích cá nhân
Điểm mạnh, yếu
Mục tiêu trong tương lai
...
||**Trên 120 từ nhé :3**||
'''
    embed.set_thumbnail(url=message.author.avatar_url)
    embed.add_field(name="**Một mẫu giới thiệu cơ bản**",value=coban,inline=False)
    await message.author.send(embed = embed)


  await client.process_commands(message)





async def fix_before_start():
      await client.wait_until_ready()
      vc_list = []
      cc_list = []
      member_list = []
######take list
      for key in db.keys():
        if "vc_id" in db[key] and "locate" in db[key]:
          member_list.append(key)
        elif "host_id" in db[key] and "vc_id" in db[key]:
          cc_list.append(key)
        elif "host_id" in db[key] and "cc_id" in db[key]:
          vc_list.append(key)

########clear member
      for key in member_list:
        check = False
        #host
        if "cc_id" in db[key]:
          guild = client.get_guild(880360143768924210)
          member = guild.get_member(int(key))
          if member == None:
            check = True
          else:          
            #voice_state = member.voice
            vc_channel = get(client.get_all_channels(), id=db[key]["vc_id"]) 
            if vc_channel != None:
              if vc_channel.members == []:
                check = True
            else:
              check = True
      #member
        else:
          guild = client.get_guild(880360143768924210)
          member = guild.get_member(int(key))
          if member == None:
            check = True
          else:          
            voice_state = member.voice
            if voice_state == None:
              check = True
            else:
              if voice_state.channel.id != db[key]["vc_id"]:
                check = True
        ########del dtb after test
        if check == True: del db[key]

########clear cc
      for key in cc_list:
        check = False
        vc_channel = get(client.get_all_channels(), id=db[key]["vc_id"])   
        cc_channel = get(client.get_all_channels(), id=int(key)) 
        if vc_channel != None:
          if vc_channel.members == []:
            if cc_channel != None:
              await cc_channel.delete()
            check = True
        else:
          if cc_channel != None:
            await cc_channel.delete()
          check = True

        if check == True: del db[key]
            

########clear vc
      for key in vc_list:
        check = False
        vc_channel = get(client.get_all_channels(), id=int(key))   
        if vc_channel != None:
          if vc_channel.members == []:
            print(vc_channel.name)
            await vc_channel.delete()
            check = True
        else:
          check = True

        if check == True: del db[key]

      print("fix done")


load_dotenv()
my_secret = os.getenv('BOT_TOKEN', "value does not exist")
client.loop.create_task(fix_before_start())
client.run(my_secret) 


