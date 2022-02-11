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


#room pos
def room_pos():
  pos = 1
  while str(pos) in db["pos"]:
    pos = pos+1
  kq = str(pos) 
  db["pos"][str(pos)] = pos
  return pos

#take invite user id
def take_data(str):
  global number
  kq = ""
  i = len(str) - 1

  while i>7:
    if str[i] in number:
      kq = str[i] + kq
      i = i - 1
    else: i=i-1

  if kq != "":
    return int(kq)


#rename
def take_name(str):
  i=9
  kq=""
  while i<len(str):
    kq = kq + str[i]
    i = i+1
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



intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)



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
m,public: mở phòng cho tất cả mọi người vào

m,private: khóa phòng, chỉ những người được mời mới vào được

m,allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

m,invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

m,disallow | m,kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

m,limit + [số_người_giới_hạn]

m,rename + [tên phòng]: đổi tên phòng

```
Hãy dùng id hoặc vào kênh <#917395775347101787> để tag tên người bạn muốn mời

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
m,public: mở phòng cho tất cả mọi người vào

m,private: khóa phòng, chỉ những người được mời mới vào được

m,hide: ẩn phòng với mọi người

m,show: hiện phòng với mọi người

m,allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

m,invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

m,disallow | m,kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

m,limit + [số_người_giới_hạn]

m,rename + [tên phòng]: đổi tên phòng

```
Hãy dùng id hoặc vào kênh <#917395775347101787> để tag tên người bạn muốn mời

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
m,public: mở phòng cho tất cả mọi người vào

m,private: khóa phòng, chỉ những người được mời mới vào được

m,allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

m,invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

m,disallow | m,kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

m,limit + [số_người_giới_hạn]

m,rename + [tên phòng]: đổi tên phòng

```
Hãy dùng id hoặc vào kênh <#900441456475508756> để tag tên người bạn muốn mời

***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ những người đang trong phòng của bạn mới thấy
-Phòng sẽ mất khi không còn ai trong phòng
||Chúc các bạn học vui =)))||
"""


command_mess_cp="""
**Các lệnh:**
```
m,public: mở phòng cho tất cả mọi người vào

m,private: khóa phòng, chỉ những người được mời mới vào được

m,hide: ẩn phòng với mọi người

m,show: hiện phòng với mọi người

m,allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

m,invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

m,disallow | m,kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

m,rename + [tên phòng]: đổi tên phòng

```
Hãy dùng id hoặc vào kênh <#901767369054109756> để tag tên người bạn muốn mời

***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ những người đang trong phòng của bạn mới thấy
-Phòng sẽ mất khi không còn ai trong phòng
||Chúc các bạn phát cơm tró vui vẻ =)))||
"""
command_mess_sa="""
**Các lệnh:**
```
m,rename + [tên phòng]: đổi tên phòng
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

#----------START-----------

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(' ')

can_clear = True
@client.event
async def on_voice_state_update(member, member_before, member_after):
  global can_clear

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
      #start_time = time.time()
      can_clear = False
      if mem_id not in db.keys():
        if check_avaiable_name(member.name) == False:
          await member.move_to(None)
          await member.send("**Bạn hãy kiểm tra và đảm bảo trong tên của bạn không có từ cấm, tục tĩu**")
        else:
          #set channel
          db[mem_id] = user_value
          #print(db[mem_id])
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
      else: 
            await member.move_to(None)
            await member.send("Bạn chỉ có thể tạo 1 phòng cùng lúc")  

      can_clear = True
      
      #end_time = time.time()
      #print('Total cre_vc time elapsed: %.4f seconds' % (end_time - start_time))



##member out
  if voice_channel_after != voice_channel_before and voice_channel_before != None:
    if str(voice_channel_before.id) in db.keys():
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
          del db[str(db[vc]["cc_id"])]
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

##member in    
  elif voice_channel_after != voice_channel_before and voice_channel_after != None:
    if str(voice_channel_after.id) in db.keys():
          wait(lambda: can_clear == True, timeout_seconds=None)
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


@client.event
async def on_message(message):
  global can_clear

  if message.author == client.user:
    return

  if message.content == "m,clear clone" or message.content == "M,clear clone":
      msg = await message.channel.send("Đợi 1 chút mình sẽ sửa lỗi")
      wait(lambda: can_clear == True, timeout_seconds=None)
      vc_list = []
      cc_list = []
      member_list = []
    ######take list
      for key in db.keys():
        check = False
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
          
      await msg.edit(content = "Lỗi đã được sửa bạn có thể tạo phòng bình thường rồi")






  if str(message.author.id) in db.keys():
    user_id = str(message.author.id)
  
    if message.content == "m,public" or message.content == "M,public" or message.content == "m, public" or message.content == "M, public":
      vc_channel = get(client.get_all_channels(), id=db[user_id]["vc_id"] )      
      overwrite = discord.PermissionOverwrite()
      overwrite.connect=True
      role = get(message.guild.roles, id=880360143768924210)
      await vc_channel.set_permissions(role, overwrite=overwrite)
      await message.channel.send("Phòng đã được mở cho mọi người vào")
  
    elif message.content=="m,private" or message.content=="M,private" or message.content=="m, private" or message.content=="M, private":
      vc_channel = get(client.get_all_channels(), id=db[user_id]["vc_id"] )     
      overwrite = discord.PermissionOverwrite()
      overwrite.connect=False
      role = get(message.guild.roles, id=880360143768924210)
      await vc_channel.set_permissions(role, overwrite=overwrite)
      await message.channel.send("Phòng đã được khóa không cho mọi người vào")
  
    elif message.content == "m,disable mic":
      pass
  
    elif message.content == "m,enable mic":
      pass     
  
    elif message.content.startswith("m,limit") or message.content.startswith("M,limit") or message.content.startswith("m, limit") or message.content.startswith("M, limit"): 
      check = db[user_id]["locate"]
      if check == "cr" or check == "ts":
        vc_channel = get(client.get_all_channels(), id=db[user_id]["vc_id"] )  
        lim = take_data(message.content)
        if lim == None:
          await message.channel.send("Bạn nhập sai cú pháp")
        elif lim == 0: await message.channel.send("Bạn không thể đặt limit phòng là 0")
        elif lim >25:
          if lim <99:
            await vc_channel.edit(user_limit= lim)
            await message.channel.send("Bạn đã đặt limit phòng: "+str(lim))
          else:
            await vc_channel.edit(user_limit=0)
            await message.channel.send("Bạn đã đặt limit phòng: Vô hạn")
          await message.channel.send("Với những phòng lim>25, bạn sẽ không thể bật được CAM")
        else:
          await vc_channel.edit(user_limit = lim)
          await message.channel.send("Bạn đã đặt limit phòng: "+str(lim))
      elif check == "sg":
        vc_channel = get(client.get_all_channels(), id=db[user_id]["vc_id"] )  
        lim = take_data(message.content)
        if lim == None:
          await message.channel.send("Bạn nhập sai cú pháp")
        elif lim == 0: await message.channel.send("Bạn không thể đặt limit phòng là 0")
        elif lim >=1 and lim <=15:
          await vc_channel.edit(user_limit= lim)
          await message.channel.send("Bạn đã đặt limit phòng: "+str(lim))
        else:
          await message.channel.send("Bạn không thể đặt limit phòng Small Group lớn hơn 15 ")
      elif check == "cp":
        await message.channel.send("Bạn không thể đặt limit cho phòng Couple")
      elif check == "sa":
        await message.channel.send("Bạn không thể đặt limit cho phòng Study Alone")
  
  
    elif message.content.startswith("m,rename") or message.content.startswith("M,rename") or message.content.startswith("m, rename") or message.content.startswith("M, rename"):
  
      msg_id = message.id
      await asyncio.sleep(0.5)
  
      if message.channel.last_message.id == msg_id:
        new_name = take_name(message.content)
        if len(new_name) > 50:
          await message.channel.send("Tên quá dài")
        else:  
          vc_channel = get(client.get_all_channels(), id=db[str(message.channel.id)]["vc_id"] ) 
          await vc_channel.edit(name=new_name)
          await message.channel.send("Tên kênh đã được đổi thành "+new_name)
      else:
        await message.channel.send("**Không được đổi tên kênh có những từ cấm nha mầy, tau táng cho á**")
  
  
  
    if message.content.startswith("m,allow") or message.content.startswith("M,allow") or message.content.startswith("m, allow") or message.content.startswith("M, allow"):
      mem_id = take_data(message.content)
      if mem_id == None :
        await message.channel.send("Bạn nhập sai cú pháp")
      else:
        guild = client.get_guild(880360143768924210)
        member = guild.get_member(mem_id)
        if member:
          vc_channel = get(client.get_all_channels(), id=db[str(message.author.id)]["vc_id"] ) 
          overwrite = discord.PermissionOverwrite()
          overwrite.view_channel=True
          overwrite.connect=True
          await vc_channel.set_permissions(member, overwrite=overwrite) 
          await message.channel.send("Đã cấp quyền cho <@"+str(mem_id)+"> vào phòng")
        else :
          await message.channel.send("Không tìm thấy người dùng")
  
        #member = message.guild.member_count
  
    elif message.content.startswith("m,invite") or message.content.startswith("M,invite") or message.content.startswith("m, invite") or message.content.startswith("M, invite"):
      mem_id = take_data(message.content)
      if mem_id == None :
        await message.channel.send("Bạn nhập sai cú pháp")
      else:
        guild = client.get_guild(880360143768924210)
        member = guild.get_member(mem_id)
        if member:
          vc_channel = get(client.get_all_channels(), id=db[str(message.author.id)]["vc_id"] ) 
          overwrite = discord.PermissionOverwrite()
          overwrite.view_channel=True
          overwrite.connect=True
          await vc_channel.set_permissions(member, overwrite=overwrite) 
          invite_link = await vc_channel.create_invite(max_uses=1,unique=True)
          await member.send("**"+str(message.author.name)+"** đã mời bạn vào học: "+str(invite_link))
          await message.channel.send("Đã mời <@"+str(mem_id)+"> vào phòng")
        else :
          await message.channel.send("Không tìm thấy người dùng")
  
    elif message.content.startswith("m,disallow") or message.content.startswith("M,disallow") or message.content.startswith("m,kick") or message.content.startswith("M,kick"):
      mem_id = take_data(message.content)
      if mem_id == None :
        await message.channel.send("Bạn nhập sai cú pháp")
      else:
        guild = client.get_guild(880360143768924210)
        member = guild.get_member(mem_id)
        if member:
          vc_channel = get(client.get_all_channels(), id=db[str(message.author.id)]["vc_id"] ) 
          if db[str(vc_channel.id)]["host_id"] != member.id:
            overwrite = discord.PermissionOverwrite()
            overwrite.connect=False
            await vc_channel.set_permissions(member, overwrite=overwrite) 
            await member.move_to(None)
            await message.channel.send("<@"+str(mem_id)+"> đã mất quyền vào phòng")
            #await message.channel.send("Do tính năng còn hạn chế nên bạn chỉ có thể kick bằng tay")
          else: await message.channel.send("Bạn không thể kick chủ phòng")
  
        else :
          await message.channel.send("Không tìm thấy người dùng")
  
    elif message.content=="m,hide" or message.content=="M,hide" or message.content=="m, hide" or message.content=="M, hide":
      check = db[user_id]["locate"]
      if check == "ts" or check == "cp":
        vc_channel = get(client.get_all_channels(), id=db[user_id]["vc_id"] )     
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel=False
        role = get(message.guild.roles, id=880360143768924210)
        await vc_channel.set_permissions(role, overwrite=overwrite)
        await message.channel.send("Phòng đã được ẩn không cho mọi người thấy")
  
    elif message.content=="m,show" or message.content=="M,show" or message.content=="m, show" or message.content=="M, show":
      check = db[user_id]["locate"]
      if check == "ts" or check == "cp":
        vc_channel = get(client.get_all_channels(), id=db[user_id]["vc_id"] )     
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel=True
        overwrite.connect=False
        role = get(message.guild.roles, id=880360143768924210)
        await vc_channel.set_permissions(role, overwrite=overwrite)
        await message.channel.send("Phòng đã được hiện cho mọi người thấy")
  

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



