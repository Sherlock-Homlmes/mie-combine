# default
import random

# lib
from discord import Interaction, app_commands
from discord.ext import commands

# local
from models import ErrandData, TopicEnum


class TopicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Topic module ready")

    async def get_topic(self, interaction: Interaction, topic: TopicEnum):
        server_info = await ErrandData.find_one(ErrandData.name == "server_info")
        if topics := server_info.value.get(topic.value):
            topic_text = random.choice(topics)
            await interaction.response.send_message(f"Chủ đề: **{topic_text}**")
        else:
            raise ValueError("Topic not found")

    @app_commands.command(name="etopic", description="Gợi ý 1 topic tiếng Anh")
    async def etopic(self, interaction: Interaction):
        await self.get_topic(interaction=interaction, topic=TopicEnum.ENG)

    @app_commands.command(name="vtopic", description="Gợi ý 1 topic tiếng Việt")
    async def vtopic(self, interaction: Interaction):
        await self.get_topic(interaction=interaction, topic=TopicEnum.VIE)


async def setup(bot):
    await bot.add_cog(TopicCog(bot))
