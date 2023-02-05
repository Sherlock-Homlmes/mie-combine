# default
import random

# lib
from discord import Interaction

# local
from bot import bot
from models import ErrandData


@bot.tree.command(name="etopic", description="Gợi ý 1 topic tiếng Anh")
async def etopic(interaction: Interaction):
    server_info = await ErrandData.find_one(ErrandData.name == "server_info")
    topics = server_info.value["etopic"]
    topic = random.choice(topics)
    await interaction.response.send_message(f"Chủ đề: **{topic}**")


@bot.tree.command(name="vtopic", description="Gợi ý 1 topic tiếng Việt")
async def vtopic(interaction: Interaction):
    server_info = await ErrandData.find_one(ErrandData.name == "server_info")
    topics = server_info.value["vtopic"]
    topic = random.choice(topics)
    await interaction.response.send_message(f"Chủ đề: **{topic}**")
