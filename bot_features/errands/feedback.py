from base import (
    #neccess
    discord, bot, get, Interaction, app_commands,
    #var
    feedback_channel_id
)

class FeedbackModal(discord.ui.Modal, title="Feedback Modal"):
    sub = discord.ui.TextInput(label="Tiêu đề")
    content = discord.ui.TextInput(label="Nội dung", style=discord.TextStyle.long)
    note = discord.ui.TextInput(label="Ghi chú(Optional)", default="không", style=discord.TextStyle.long, required=False)

    async def on_submit(self, interaction: Interaction, /) -> None:
        feedback_channel = get(bot.get_all_channels(), id=feedback_channel_id)
        last_message = await feedback_channel.fetch_message(feedback_channel.last_message_id)
        
    
        try:
            feedback_number = int(last_message.content.replace('**-----Feedback ','').replace('-----*','').split("*")[0]) + 1
        except discord.errors.NotFound:
            feedback_number = ""
            await feedback_channel.send("**Cảnh báo: feedback trước đó đã bị xóa**")

        message = f'''
**-----Feedback {feedback_number}-----**
**From:** {interaction.user.mention}
**Title:** {self.sub}
```
{self.content} 
```
**Note:** {self.note}
'''   
        await feedback_channel.send(message)
        await interaction.response.send_message("Cảm ơn bạn đã gửi feedback cho chúng mình", ephemeral=True)


@bot.tree.command(name="feedback", description="Gửi góp ý, báo cáo về cho chúng mình")
async def testmodal(interaction: Interaction):
    await interaction.response.send_modal(FeedbackModal())