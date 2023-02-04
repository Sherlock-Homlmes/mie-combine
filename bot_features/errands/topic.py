from base import (
    # necess
    bot,
    tasks,
    get,
    Interaction,
    # var
    color_roles,
)

import random

from other_modules.stable_json import open_database


@bot.tree.command(name="etopic", description="Gợi ý 1 topic tiếng Anh")
async def etopic(interaction: Interaction):
    topic = random.choice(open_database("/topic/etopic"))
    await interaction.response.send_message(f"Chủ đề: **{topic}**")


@bot.tree.command(name="vtopic", description="Gợi ý 1 topic tiếng Việt")
async def vtopic(interaction: Interaction):
    topic = random.choice(open_database("/topic/vtopic"))
    await interaction.response.send_message(f"Chủ đề: **{topic}**")
