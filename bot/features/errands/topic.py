# default
import random

# lib
from discord import Interaction

# local
from bot import bot
from models import ErrandData, TopicEnum


async def get_topic(interaction: Interaction, topic: TopicEnum):
    server_info = await ErrandData.find_one(ErrandData.name == "server_info")
    if topics := server_info.value.get(topic.value):
        topic = random.choice(topics)
        await interaction.response.send_message(f"Chủ đề: **{topic}**")
    else:
        # TODO
        raise


@bot.tree.command(name="etopic", description="Gợi ý 1 topic tiếng Anh")
async def etopic(interaction: Interaction):
    await get_topic(interaction=interaction, topic=TopicEnum.ENG)


@bot.tree.command(name="vtopic", description="Gợi ý 1 topic tiếng Việt")
async def vtopic(interaction: Interaction):
    await get_topic(interaction=interaction, topic=TopicEnum.VIE)
