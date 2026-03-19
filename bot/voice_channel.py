import discord

from core.conf.bot.conf import bot


@bot.tree.command(name="join", description="Bot join voice channel của mày")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message(
            "Mày phải vào voice channel trước đã!", ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect()

    await interaction.response.send_message("Hê nô 👋")


@bot.tree.command(name="leave", description="Bot rời voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message(
            "Tao đang không ở trong room nào!", ephemeral=True
        )
        return

    await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message("Bye 👋")
