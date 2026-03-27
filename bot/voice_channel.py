import discord
from discord import app_commands
from discord.ext import commands

from utils.discord_bot.check import is_admin


class VoiceChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Voice channel module ready")

    @app_commands.command(name="join", description="Bot join voice channel của mày")
    @app_commands.check(is_admin)
    async def join(self, interaction: discord.Interaction):
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

    @app_commands.command(name="leave", description="Bot rời voice channel")
    @app_commands.check(is_admin)
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            await interaction.response.send_message(
                "Tao đang không ở trong room nào!", ephemeral=True
            )
            return

        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Bye 👋")


async def setup(bot):
    await bot.add_cog(VoiceChannelCog(bot))
