from base import (
  # necess
  bot,tasks,get,
  # var
  color_roles
  )


@bot.command(name="color")
async def color(ctx,arg):
  check = True
  try:
    color = int(arg)
  except Exception as e:
    check = False    

  if check == False or color > len(color_roles):
    await ctx.send("Chọn sai số màu")
  else:
    user = ctx.author
    role_names = [role.name for role in user.roles]
    if "HOMIE" in role_names or "HỌC SINH TÍCH CỰC" in role_names:
        if "COLOR" in role_names:
          pos = role_names.index("COLOR")
          role_ids = [role.id for role in user.roles]
          color_old = get(user.guild.roles, id=role_ids[pos])
          await user.remove_roles(color_old)
          
        color_new = get(user.guild.roles, id=color_roles[color-1])
        await user.add_roles(color_new)
        await ctx.channel.send(f"Bạn đã đổi sang màu **{color}** thành công")

    else: 
      await ctx.channel.send("Bạn chưa có role HOMIE hoặc HSTC để đổi màu")

@bot.command(name="rmcolor")
async def color(ctx):
  user = ctx.author
  role_names = [role.name for role in user.roles]
  if "COLOR" in role_names:
    pos = role_names.index("COLOR")
    role_ids = [role.id for role in user.roles]
    color_old = get(user.guild.roles, id=role_ids[pos])
    await user.remove_roles(color_old)
  await ctx.channel.send("Bạn đã bỏ role màu")