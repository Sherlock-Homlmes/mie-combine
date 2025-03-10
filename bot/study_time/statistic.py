# default
import asyncio
import math
from typing import Optional, List
import random
import copy

# lib
import discord
from discord import app_commands
import pymongo
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel
from cache import AsyncTTL

# local
from core.conf.bot.conf import bot
from core.models import UserDailyStudyTimes, Users
from utils.time_modules import Now
from utils.image_handle import save_image


@bot.tree.command(name="member_study_time")
@app_commands.describe(member="Member")
@app_commands.default_permissions(administrator=True)
async def member_study_time(interaction: discord.Interaction, member: discord.Member):
    user_daily_study_time = await UserDailyStudyTimes.find(
        UserDailyStudyTimes.user_discord_id == member.id
    ).to_list()
    total_time = sum([sum(x.study_time) for x in user_daily_study_time])
    if not total_time:
        total_time = 0

    if total_time:
        content = f"Tổng thời gian học: {total_time//60}h {total_time%60}'"
    else:
        content = "Bạn chưa học trong BetterMe"
    await interaction.response.send_message(content)


@bot.tree.command(name="study_time", description="Xem tổng thời gian học")
async def study_time(interaction: discord.Interaction):
    user_daily_study_time = await UserDailyStudyTimes.find(
        UserDailyStudyTimes.user_discord_id == interaction.user.id
    ).to_list()
    total_time = sum([sum(x.study_time) for x in user_daily_study_time])
    if not total_time:
        total_time = 0
    if total_time:
        content = f"Tổng thời gian học: {total_time//60}h {total_time%60}'"
    else:
        content = "Bạn chưa học trong BetterMe"
    await interaction.response.send_message(content)


@bot.tree.command(name="daily", description="Xem thời gian học hôm nay")
async def daily(interaction: discord.Interaction):
    total_time = await UserDailyStudyTimes.find_one(
        UserDailyStudyTimes.user_discord_id == interaction.user.id,
        UserDailyStudyTimes.date == Now().today,
    )
    if total_time:
        content = f"Thời gian học hôm nay: {total_time.study_time}"
    else:
        total_time = [0] * 24
        content = "Bạn chưa học hôm nay"

    await interaction.response.send_message(content)


data_format_infos_top = [
    # top 3
    {
        "img_position": (1162, 497),
        "img_size": 490,
        "text_position": (1400, 1115),
        "text_font_size": 70,
        "text_max_width": 650,
        "text_format_type": "CENTER",
        "time_position": (1400, 1200),
        "time_font_size": 50,
    },
    {
        "img_position": (512, 543),
        "img_size": 377,
        "text_position": (700, 1115),
        "text_font_size": 70,
        "text_max_width": 650,
        "text_format_type": "CENTER",
        "time_position": (700, 1200),
        "time_font_size": 50,
    },
    {
        "img_position": (1922, 543),
        "img_size": 377,
        "text_position": (2100, 1115),
        "text_font_size": 70,
        "text_max_width": 650,
        "text_format_type": "CENTER",
        "time_position": (2100, 1200),
        "time_font_size": 50,
    },
    # top 10
    {
        "img_position": (111, 1427),
        "img_size": 188,
        "text_position": (625, 1482),
        "text_font_size": 70,
        "text_max_width": None,
        "text_format_type": None,
        "time_position": (2200, 1482),
        "time_font_size": 70,
    },
    {
        "img_position": (111, 1640),
        "img_size": 188,
        "text_position": (625, 1695),
        "text_font_size": 70,
        "text_max_width": None,
        "text_format_type": None,
        "time_position": (2200, 1695),
        "time_font_size": 70,
    },
    {
        "img_position": (111, 1853),
        "img_size": 188,
        "text_position": (625, 1908),
        "text_font_size": 70,
        "text_max_width": None,
        "text_format_type": None,
        "time_position": (2200, 1908),
        "time_font_size": 70,
    },
    {
        "img_position": (111, 2066),
        "img_size": 188,
        "text_position": (625, 2121),
        "text_font_size": 70,
        "text_max_width": None,
        "text_format_type": None,
        "time_position": (2200, 2121),
        "time_font_size": 70,
    },
    {
        "img_position": (111, 2279),
        "img_size": 188,
        "text_position": (625, 2334),
        "text_font_size": 70,
        "text_max_width": None,
        "text_format_type": None,
        "time_position": (2200, 2334),
        "time_font_size": 70,
    },
    {
        "img_position": (111, 2492),
        "img_size": 188,
        "text_position": (625, 2547),
        "text_font_size": 70,
        "text_max_width": None,
        "text_format_type": None,
        "time_position": (2200, 2547),
        "time_font_size": 70,
    },
    {
        "img_position": (111, 2706),
        "img_size": 188,
        "text_position": (625, 2760),
        "text_font_size": 70,
        "text_max_width": None,
        "text_format_type": None,
        "time_position": (2200, 2760),
        "time_font_size": 70,
    },
]

data_format_info = {
    "img_position": [115, 725],
    "img_size": 188,
    "idx_text_position": [440, 784],
    "idx_text_font_size": 70,
    "text_position": [718, 784],
    "text_font_size": 70,
    "text_max_width": None,
    "text_format_type": None,
    "time_position": [2200, 784],
    "time_font_size": 70,
}


def convert_text(text: str, text_font: int, max_width: Optional[int] = None) -> tuple[int, int]:
    if not max_width:
        return text
    text_count = len(text)
    text_width = text_count * text_font / 2.5
    one_word_width = text_font / 3
    if text_width < max_width:
        return text
    cut_string = math.ceil((text_width - max_width) / one_word_width + 1)
    return text[:-cut_string] + "..."


# TODO: to center_y_position
def calculate_position(
    center_x_position: int, y_position: int, text: str, text_font: int
) -> tuple[int, int]:
    text = convert_text(text, text_font, 650)
    text_count = len(text)
    text_width = text_count * text_font / 2
    return (center_x_position - text_width / 2, y_position)


def generate_leaderboard_image(
    leaderboard_data: dict,
    start_idx: int,
    target_idx: Optional[int] = None,
    img_path: Optional[str] = None,
) -> str:
    is_top = start_idx == 0
    foreground_img = Image.open(
        "./assets/top_leaderboard.png" if is_top else "./assets/leaderboard.png"
    )
    final_img = Image.new("RGBA", foreground_img.size)
    d = ImageDraw.Draw(final_img)

    fonts = {
        50: ImageFont.truetype("./assets/Roboto-Bold.ttf", 50),
        70: ImageFont.truetype("./assets/Roboto-ExtraBold.ttf", 75),
        90: ImageFont.truetype("./assets/Roboto-ExtraBold.ttf", 90),
    }

    for data in leaderboard_data:
        img_pos = data["img_position"]
        img_size = data["img_size"]
        user_avatar = Image.open(data["img"])
        user_avatar = user_avatar.resize((img_size, img_size))
        final_img.paste(user_avatar, img_pos)
    final_img.paste(foreground_img, (0, 0), foreground_img)
    for idx, data in enumerate(leaderboard_data):
        # TODO: do this
        # if not is_top and target_idx - start_idx == idx:
        #     print(target_idx, start_idx, target_idx - start_idx, idx)
        #     target_row =  Image.open("./assets/target_row.png")
        #     img_pos = data["img_position"]
        #     final_img.paste(target_row, (img_pos[0]+60, img_pos[1]+10))
        text_pos = data["text_position"]
        text = data["text"]
        time_pos = data["time_position"]
        time_text = data["time"]
        user_name_font = fonts[data["text_font_size"]]
        user_name_color = (255, 255, 255) if not is_top or idx > 2 else (224, 174, 51)
        time_font = fonts[data["time_font_size"]]
        d.text(text_pos, text, font=user_name_font, fill=user_name_color)
        d.text(time_pos, time_text, font=time_font, fill=(255, 255, 255))
        if data.get("idx_text"):
            d.text(
                data["idx_text_position"],
                data["idx_text"],
                font=fonts[data["idx_text_font_size"]],
                fill=(255, 255, 255),
            )

    if img_path is None:
        img_path = f"./assets/cache/{random.randint(1, 1000000)}"
    final_img.save(img_path)
    return img_path


class LeaderboardInfo(BaseModel):
    content: str
    img_path: str
    member_ids: List[int]


@AsyncTTL(time_to_live=60)
async def generate_leaderboard_info(
    time_range: str, member_id: Optional[int] = None
) -> LeaderboardInfo:
    # Aggregation pipeline to calculate total study time per user for the current month
    pipeline = [
        {
            "$group": {
                "_id": "$user_discord_id",
                "total_study_time": {"$sum": {"$sum": "$study_time"}},
            }
        },
        {"$sort": {"total_study_time": pymongo.DESCENDING}},
    ]
    if not member_id:
        pipeline.append({"$limit": 10})

    time_module = Now()
    if time_range == "Tất cả":
        content = "Leaderboard server Betterme"
        img_name = "all.png"
    elif time_range == "Tháng này":
        content = f"Leaderboard tháng {time_module.now.month}/{time_module.now.year}"
        month_start = time_module.first_day_of_month()
        month_end = time_module.last_day_of_month()
        img_name = "month.png"
        pipeline.insert(
            0,
            {
                "$match": {
                    "date": {"$gte": month_start, "$lte": month_end},
                }
            },
        )
    elif time_range == "Tuần này":
        week_start = time_module.first_day_of_week()
        week_end = time_module.last_day_of_week()
        content = "Leaderboard tuần này"
        img_name = "week.png"
        pipeline.insert(
            0,
            {
                "$match": {
                    "date": {"$gte": week_start, "$lte": week_end},
                }
            },
        )
    elif time_range == "Hôm nay":
        content = "Leaderboard hôm nay"
        today = time_module.today
        img_name = "today.png"
        pipeline.insert(
            0,
            {
                "$match": {
                    "date": {"$eq": today},
                }
            },
        )

    results = await UserDailyStudyTimes.aggregate(pipeline).to_list()
    target_idx = None
    start_idx = None
    if member_id:
        try:
            target_idx = next(
                i for i, item in enumerate(results) if item["_id"] == member_id
            )
        except StopIteration:
            # TODO: fix this exception
            raise ValueError()
        start_idx = target_idx // 10 * 10
        end_idx = min([len(results) - 1, start_idx + 10])
        results = results[start_idx:end_idx]
        img_name = f"page-{start_idx//10+1}-" + img_name
    else:
        img_name = "page-1-" + img_name

    users = await asyncio.gather(
        *[Users.find_one({Users.discord_id: str(result["_id"])}) for result in results]
    )
    users_avatar = await asyncio.gather(
        *[
            save_image(
                user.avatar, target_path=f"./assets/cache/{user.discord_id}.png", use_cache=True
            )
            for user in users
        ]
    )

    for idx, result in enumerate(results):
        if start_idx == 0:
            data_info = data_format_infos_top[idx]
        else:
            data_info = copy.deepcopy(data_format_info)
            data_info["img_position"][1] += 213 * idx
            data_info["idx_text_position"][1] += 213 * idx
            data_info["text_position"][1] += 213 * idx
            data_info["time_position"][1] += 213 * idx

        total_time_hour = result["total_study_time"] // 60
        total_time_min = result["total_study_time"] % 60
        total_study_time = f'{total_time_hour}:{total_time_min if total_time_min >= 10 else "0" + str(total_time_min)}'

        result["_id"] = str(result["_id"])
        result["img"] = users_avatar[idx] if users_avatar[idx] else "./assets/default_avatar.png"
        result["img_position"] = data_info["img_position"]
        result["img_size"] = data_info["img_size"]

        if data_info["text_format_type"] == "CENTER":
            result["text_position"] = calculate_position(
                data_info["text_position"][0],
                data_info["text_position"][1],
                users[idx].name,
                data_info["text_font_size"],
            )
            result["text"] = convert_text(
                users[idx].name, data_info["text_font_size"], data_info["text_max_width"]
            )
        else:
            result["text_position"] = data_info["text_position"]
            result["text"] = users[idx].nick if users[idx].nick else users[idx].name
        result["text_font_size"] = data_info["text_font_size"]
        
        if data_info.get("idx_text"):
            result["idx_text_position"] = data_info["idx_text_position"]
            result["idx_text"] = str(start_idx + idx + 1)
            result["idx_text_font_size"] = data_info["idx_text_font_size"]

        result["time_position"] = calculate_position(
            data_info["time_position"][0],
            data_info["time_position"][1],
            total_study_time,
            data_info["time_font_size"],
        )
        result["time"] = total_study_time
        result["time_font_size"] = data_info["time_font_size"]

    img_path = f"./assets/cache/{img_name}"
    generate_leaderboard_image(
        leaderboard_data=results, start_idx=start_idx, target_idx=target_idx, img_path=img_path
    )

    return LeaderboardInfo(
        content=content, img_path=img_path, member_ids=[user.discord_id for user in users]
    )


@bot.tree.command(name="leaderboard", description="Bảng xếp hạng thời gian học")
@app_commands.describe(time_range="Khoảng thời gian")
@app_commands.choices(
    time_range=[
        app_commands.Choice(name="Tất cả", value=1),
        app_commands.Choice(name="Tháng này", value=2),
        app_commands.Choice(name="Tuần này", value=3),
        app_commands.Choice(name="Hôm nay", value=4),
    ]
)
async def leaderboard(interaction: discord.Interaction, time_range: app_commands.Choice[int]):
    await interaction.response.defer()
    # BUG: last one in list
    try:
        leaderboard_info = await generate_leaderboard_info(
            time_range.name, member_id=interaction.user.id
        )
        with open(leaderboard_info.img_path, "rb") as f:
            await interaction.followup.send(content=leaderboard_info.content, file=discord.File(f))
    except ValueError:
        await interaction.followup.send(content="Bạn chưa học trong khoảng thời gian này")
