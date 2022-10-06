from base import (
  # necess
  bot,tasks,get,
  # var
  guild_id,
  cap3day, thptday,cap3_channel_id,thpt_channel_id,
  total_mem_channel_id,online_mem_channel_id,study_count_channel_id
  )


import requests
import datetime
from datetime import timedelta
import pytz
from math import trunc

total_member = 10000
online_member = 1000

@tasks.loop(minutes=6)
async def static_channels():
  global online_member, total_member

  await bot.wait_until_ready()

  # count down
  cap3_channel = await bot.fetch_channel(cap3_channel_id)
  thpt_channel = await bot.fetch_channel(thpt_channel_id)

  utc_now = pytz.utc.localize(datetime.datetime.utcnow())
  pst_now = utc_now.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
  today =  datetime.datetime(pst_now.year , pst_now.month , pst_now.day, pst_now.hour)
  
  cap3_left = cap3day - today - timedelta(hours=1)
  thpt_left = thptday - today - timedelta(hours=1)

  thpt = 'THPT: '+str(thpt_left.days)+' ngày '+str(trunc(thpt_left.seconds/3600))+' giờ '
  cap3 = 'Cấp 3: '+str(cap3_left.days)+' ngày '+str(trunc(cap3_left.seconds/3600))+' giờ '   

  await cap3_channel.edit(name=cap3)
  await thpt_channel.edit(name=thpt)

  # server spec
  total_mem_channel = await bot.fetch_channel(total_mem_channel_id)
  online_mem_channel = await bot.fetch_channel(online_mem_channel_id)
  study_count_channel = await bot.fetch_channel(study_count_channel_id)

  resp = requests.get('https://discord.com/api/guilds/880360143768924210/widget.json')
  resp = resp.json()
  online_member = resp["presence_count"]

  guild = bot.get_guild(guild_id)
  voice_channel_list = guild.voice_channels
  total_voice_member = 0
  for channel in voice_channel_list:
    total_voice_member += len(channel.members)
  total_member = guild.member_count

  await total_mem_channel.edit(name = f"Thành viên: {total_member} người")
  await online_mem_channel.edit(name = f"Online: {online_member} người")
  await study_count_channel.edit(name = f"Đang học: {total_voice_member} người")
  print("done")

def member_info():
  global total_member, online_member

  return (total_member, online_member)
