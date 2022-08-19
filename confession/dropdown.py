@bot.command(name="faq")
async def faq(ctx):
    if ctx.author.id in admin_id:

      await ctx.send(embed=embed)
      question= discord.utils.get(bot.emojis, name='ques_1')
      confession= discord.utils.get(bot.emojis, name='confession')
      await ctx.send("**Những câu hỏi thường gặp**",
    components = [
    Select(
        placeholder= "FAQ",
        #max_values=3,
        options=[
            SelectOption(
              label="Bỏ chọn",
              value="none",),
            SelectOption(
              label="BetterMe là gì vậy?",
              value="betterme",
              emoji=question),
            SelectOption(
              label="Mình không biết dùng Discord",
              value="discord use",
              emoji=question),
            SelectOption(
              label="Cách vào phòng học",
              value="how to study",
              emoji=question),         
            SelectOption(
              label="Cách bật BOT nhạc?",
              value="how to music",
              emoji=question),  
        ]
      )])


@bot.event
async def on_select_option(interaction):
    global url

####game
    if interaction.message.id == 924948037439225867: #Message id(not obligatory)
      await interaction.respond(type=6)

      if "none game" in interaction.values:
        khu_vui_choi = discord.utils.get(interaction.guild.roles, id=923963988784590920)
        await interaction.author.remove_roles(khu_vui_choi) 
        tarot = discord.utils.get(interaction.guild.roles, id=924740298062561343)
        await interaction.author.remove_roles(tarot)   
        sudoku = discord.utils.get(interaction.guild.roles, id=924749171142037504)
        await interaction.author.remove_roles(sudoku) 
        owo = discord.utils.get(interaction.guild.roles, id=924750666512089178)
        await interaction.author.remove_roles(owo)     
        new_msg = await interaction.message.channel.send("**"+interaction.author.mention+" đã chọn không chơi game**")    
        await asyncio.sleep(10)
        await new_msg.delete()

      elif "game all" in interaction.values:
        khu_vui_choi = discord.utils.get(interaction.guild.roles, id=923963988784590920)
        await interaction.author.add_roles(khu_vui_choi) 

        tarot = discord.utils.get(interaction.guild.roles, id=924740298062561343)
        await interaction.author.remove_roles(tarot)   
        sudoku = discord.utils.get(interaction.guild.roles, id=924749171142037504)
        await interaction.author.remove_roles(sudoku) 
        owo = discord.utils.get(interaction.guild.roles, id=924750666512089178)
        await interaction.author.remove_roles(owo) 

        new_msg = await interaction.message.channel.send("**"+interaction.author.mention+" đã chọn chơi tất cả mọi game**")  
        await asyncio.sleep(10)
        await new_msg.delete()

      elif "sudoku" in interaction.values and "tarot" in interaction.values and "owo" in interaction.values:
        khu_vui_choi = discord.utils.get(interaction.guild.roles, id=923963988784590920)
        await interaction.author.add_roles(khu_vui_choi) 

        tarot = discord.utils.get(interaction.guild.roles, id=924740298062561343)
        await interaction.author.remove_roles(tarot)   
        sudoku = discord.utils.get(interaction.guild.roles, id=924749171142037504)
        await interaction.author.remove_roles(sudoku) 
        owo = discord.utils.get(interaction.guild.roles, id=924750666512089178)
        await interaction.author.remove_roles(owo) 

        new_msg = await interaction.message.channel.send("**"+interaction.author.mention+" đã chọn chơi tất cả mọi game**") 
        await asyncio.sleep(10)
        await new_msg.delete()

      else:
        khu_vui_choi = discord.utils.get(interaction.guild.roles, id=923963988784590920)
        await interaction.author.remove_roles(khu_vui_choi) 
        #inter = await interaction.author.remove_roles(khu_vui_choi) 
        #labels = [option.label for option in inter.Select.selected_options]
        
        game = ""
        if "sudoku" in interaction.values:
          sudoku = discord.utils.get(interaction.guild.roles, id=924749171142037504)
          await interaction.author.add_roles(sudoku) 
          game = game + "Sudoku,"
        else:
          sudoku = discord.utils.get(interaction.guild.roles, id=924749171142037504)
          await interaction.author.remove_roles(sudoku) 


        if "tarot" in interaction.values:
          tarot = discord.utils.get(interaction.guild.roles, id=924740298062561343)
          await interaction.author.add_roles(tarot) 
          game = game + "Tarot,"  
        else:
          tarot = discord.utils.get(interaction.guild.roles, id=924740298062561343)
          await interaction.author.remove_roles(tarot)   

        if "owo" in interaction.values:
          owo = discord.utils.get(interaction.guild.roles, id=924750666512089178)
          await interaction.author.add_roles(owo)  
          game = game + "OwO"
        else:
          owo = discord.utils.get(interaction.guild.roles, id=924750666512089178)
          await interaction.author.remove_roles(owo)  

        new_msg = await interaction.message.channel.send("**"+interaction.author.mention+" đã chọn chơi: "+game+"**") 
        await asyncio.sleep(10)
        await new_msg.delete()

####FAQ
    elif interaction.message.id == 925418736431792169:
      await interaction.respond(type=6)
      
      if "betterme" in interaction.values:

        v1 = "BetterMe là Cộng Đồng học tập trên Discord dành cho người Việt hoạt động trên nền tảng Discord"
        v2 = "Hoạt động chủ yếu theo cách ``study with me``. Mọi người vào phòng học cùng bạn bè hoặc những bạn khác trong server"
        v3 = "Hãy nhắn vào kênh <#880360237436121120>"
        faq_channel = get(interaction.guild.channels, id=880360237436121120)
        embed= discord.Embed(
        title =  "**BetterMe là gì?**",
        colour = discord.Colour.gold())

        embed.add_field(name="**Câu hỏi của**",value="||"+interaction.author.mention+"||" ,inline=False)
        embed.add_field(name="**Giới thiệu về BetterMe**",value=v1,inline=False)
        embed.add_field(name="**Cách thức hoạt động?**",value=v2,inline=False)
        embed.add_field(name="**Bạn có thắc mắc về bất kì vấn đề gì?**",value=v3,inline=False)
        embed.set_image(url="https://i.ibb.co/Wvw2CY9/Betterme.png")
        embed.set_footer(text='''BetterMe - Better everyday''')

        msg = await faq_channel.send(embed=embed)
        await asyncio.sleep(60)
        await msg.delete()
      elif "discord use" in interaction.values:
        faq_channel = get(interaction.guild.channels, id=880360237436121120)
        embed= discord.Embed(
        title =  "**Mình chưa biết sử dụng Discord**",
        description = "Ở kênh <#915949063403347968> có hướng dẫn sử dụng đó. Nếu bạn xem vẫn không hiểu thì nhắn vào <#880360237436121120> nha",
        colour = discord.Colour.gold())

        embed.add_field(name="**Câu hỏi của**",value="||"+interaction.author.mention+"||" ,inline=False)
        embed.set_image(url="https://i.ibb.co/Wvw2CY9/Betterme.png")
        embed.set_footer(text='''BetterMe - Better everyday''')

        msg = await faq_channel.send(embed=embed)
        await asyncio.sleep(60)
        await msg.delete()
      elif "how to study" in interaction.values:
        faq_channel = get(interaction.guild.channels, id=880360237436121120)
        embed= discord.Embed(
        title =  "**Cách vào phòng học**",
        description = "Ở kênh <#915949063403347968> có hướng dẫn đó.",
        colour = discord.Colour.gold())

        embed.add_field(name="**Câu hỏi của**",value="||"+interaction.author.mention+"||" ,inline=False)
        embed.set_image(url="https://i.ibb.co/Wvw2CY9/Betterme.png")
        embed.set_footer(text='''BetterMe - Better everyday''')

        msg = await faq_channel.send(embed=embed)
        await asyncio.sleep(60)
        await msg.delete()
      elif "how to music" in interaction.values:
        faq_channel = get(interaction.guild.channels, id=880360237436121120)
        embed= discord.Embed(
        title =  "**Cách bật BOT nhạc**",
        description ='''
Ở kênh <#884802950759866428> có hướng dẫn sử dụng đó.
VD: ``m!play we don't talk anymore`` hoặc ``m!play https://www.youtube.com/watch?v=3AtDnEC4zak``
Nếu bạn xem vẫn không hiểu thì nhắn vào <#880360237436121120> nha''',
        colour = discord.Colour.gold())

        embed.add_field(name="**Câu hỏi của**",value="||"+interaction.author.mention+"||" ,inline=False)
        embed.set_image(url="https://i.ibb.co/Wvw2CY9/Betterme.png")
        embed.set_footer(text='''BetterMe - Better everyday''')

        msg = await faq_channel.send(embed=embed)
        await asyncio.sleep(90)
        await msg.delete()
