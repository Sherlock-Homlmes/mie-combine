# default
import asyncio
import copy
import json
import math
import random
from typing import List, Optional
from urllib.parse import urlencode

# lib
import discord
import pymongo
from cache import AsyncTTL
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel
from quickchart import QuickChart

# local
from core.conf.bot.conf import bot
from core.models import UserDailyStudyTimes, Users
from utils.image_handle import save_image
from utils.time_modules import Now, generate_date_strings


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


async def generate_member_study_time_image(
    member_id: int, time_range: Optional[str] = "Tất cả"
) -> str:
    time_module = Now()
    sub_labels = []
    time_range_date_map = {
        "Tất cả": {
            "start_date": None,
            "end_date": None,
        },
        "Tháng này": {
            "start_date": time_module.first_day_of_last_month(),
            "end_date": time_module.last_day_of_month(),
        },
        "Tuần này": {
            "start_date": time_module.first_day_of_last_week(),
            "end_date": time_module.last_day_of_week(),
        },
        "Hôm nay": {
            "start_date": time_module.some_day_before(1),
            "end_date": time_module.today,
        },
    }
    start_date = time_range_date_map[time_range]["start_date"]
    end_date = time_range_date_map[time_range]["end_date"]
    study_time_stats = await UserDailyStudyTimes.get_user_study_time_stats(
        member_id, start_date, end_date
    )
    if study_time_stats.total == 0:
        raise ValueError("No data")

    labels = []
    sub_labels = []
    data = []
    data2 = []
    total_time = 0
    total_past_time = 0
    chart_legend_label = ""
    chart_legend_label2 = ""

    max_value = 24
    file_path = "./assets/cache/"

    if time_range == "Tất cả":
        pass
    elif time_range == "Tháng này":
        file_path += f"{member_id}-month.png"

        first_day_of_last_month = start_date
        last_day_of_last_month = time_module.last_day_of_last_month()
        first_day_of_this_month = time_module.first_day_of_month()
        last_day_of_this_month = end_date
        study_time_date_data = study_time_stats.daily_study_time_to_object()

        labels = generate_date_strings(first_day_of_this_month, last_day_of_this_month)
        for label in labels:
            data.append(sum(study_time_date_data.get(label, [])) / 60)
            total_time += sum(study_time_date_data.get(label, []))
        chart_legend_label = f"Tháng này: {total_time//60} giờ {total_time%60} phút"

        labels2 = generate_date_strings(first_day_of_last_month, last_day_of_last_month)
        for label in labels2:
            data2.append(sum(study_time_date_data.get(label, [])) / 60)
            total_past_time += sum(study_time_date_data.get(label, []))
        chart_legend_label2 = (
            f"Tháng trước: {total_past_time//60} giờ {total_past_time%60} phút"
        )

    elif time_range == "Tuần này":
        file_path += f"{member_id}-week.png"
        labels = ["M", "T", "W", "T", "F", "S", "S"]

        first_day_of_last_week = start_date
        last_day_of_last_week = time_module.last_day_of_last_week()
        first_day_of_this_week = time_module.first_day_of_week()
        last_day_of_this_week = end_date
        study_time_date_data = study_time_stats.daily_study_time_to_object()

        sub_labels = generate_date_strings(
            first_day_of_this_week, last_day_of_this_week
        )
        for label in sub_labels:
            data.append(sum(study_time_date_data.get(label, [])) / 60)
            total_time += sum(study_time_date_data.get(label, []))
        chart_legend_label = f"Tuần này: {total_time//60} giờ {total_time%60} phút"

        labels2 = generate_date_strings(first_day_of_last_week, last_day_of_last_week)
        for label in labels2:
            data2.append(sum(study_time_date_data.get(label, [])) / 60)
            total_past_time += sum(study_time_date_data.get(label, []))
        chart_legend_label2 = (
            f"Tuần trước: {total_past_time//60} giờ {total_past_time%60} phút"
        )
    elif time_range == "Hôm nay":
        file_path += f"{member_id}-today.png"
        max_value = 60
        labels = [str(i) for i in range(0, 24)]

        study_time_date_data = study_time_stats.daily_study_time_to_object()

        date_strings = generate_date_strings(
            time_module.some_day_before(1), time_module.today
        )
        data = study_time_date_data.get(date_strings[1], [])
        data2 = study_time_date_data.get(date_strings[0], [])
        total_time = sum(data)
        total_past_time = sum(data2)
        chart_legend_label = f"Hôm nay: {total_time//60} giờ {total_time%60} phút"
        chart_legend_label2 = (
            f"Hôm qua: {total_past_time//60} giờ {total_past_time%60} phút"
        )

    max_data_value = max(data)
    step_size = max_data_value // 5

    qc = QuickChart()
    qc.width = 500
    qc.height = 300
    qc.device_pixel_ratio = 2.0
    config = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": chart_legend_label,
                    "backgroundColor": "rgb(221, 178, 29)",
                    "data": data,
                    "borderRadius": 100,
                    "borderSkipped": False,
                },
            ],
        },
        "options": {
            "plugins": {
                "legend": {
                    "position": "bottom",
                    "labels": {
                        "usePointStyle": True,
                        "pointStyle": "rectRounded",
                    },
                },
            },
            "scales": {
                "x": {
                    "stacked": True,
                    "grid": {
                        "display": False,
                        "drawTicks": False,
                    },
                    "ticks": {
                        "color": "rgba(255, 255, 255, 1)",
                    },
                },
                "y": {
                    "grid": {
                        "display": True,
                        "lineWidth": 4,
                        "color": "rgb(4, 34, 49)",
                        "drawTicks": False,
                        "tickBorderDash": [10],
                    },
                    "min": 0,
                    "max": max_value
                    if max_data_value - step_size > max_value * 4 / 5
                    else None,
                    "ticks": {
                        "color": "rgba(255, 255, 255, 1)",
                        "stepSize": step_size,
                    },
                    "drawOnChartArea": False,
                },
            },
        },
    }
    if len(sub_labels):
        config["options"]["scales"]["x2"] = {
            "labels": sub_labels,
        }
    if len(data2):
        len_list1 = len(data)
        len_list2 = len(data2)
        if len_list1 > len_list2:
            data2.extend([0] * (len_list1 - len_list2))
        elif len_list2 > len_list1:
            data2 = data2[:len_list1]
        config["data"]["datasets"].append(
            {
                "label": chart_legend_label2,
                "backgroundColor": "rgb(45, 99, 117)",
                "data": data2,
                "borderRadius": 100,
                "borderSkipped": False,
            }
        )

    params = {
        "chart": json.dumps(config),
        "width": 500,
        "height": 300,
        "backgroundColor": "rgb(5, 25, 35)",
        "version": 4,
    }
    await save_image(f"https://quickchart.io/chart?{urlencode(params)}", file_path)

    chart_img = Image.open(file_path)
    final_img = Image.new("RGBA", (1100, 650), (5, 25, 35))
    final_img.paste(chart_img, (50, 50))
    final_img.save(file_path)
    return file_path


@bot.tree.command(name="study_time", description="Xem tổng thời gian học")
@app_commands.describe(time_range="Khoảng thời gian")
@app_commands.choices(
    time_range=[
        # app_commands.Choice(name="Tất cả", value=1),
        app_commands.Choice(name="Tháng này", value=2),
        app_commands.Choice(name="Tuần này", value=3),
        app_commands.Choice(name="Hôm nay", value=4),
    ]
)
async def study_time(
    interaction: discord.Interaction, time_range: app_commands.Choice[int]
):
    await interaction.response.defer()

    try:
        statistic_path = await generate_member_study_time_image(
            interaction.user.id, time_range.name
        )
        with open(statistic_path, "rb") as f:
            await interaction.followup.send(file=discord.File(f))
    except ValueError:
        await interaction.followup.send(
            content="Bạn chưa học trong khoảng thời gian này"
        )


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


def convert_text(
    text: str, text_font: int, max_width: Optional[int] = None
) -> tuple[int, int]:
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
        # TODO: fix: missing number in top 10 leaderboard
        if (
            target_idx
            and target_idx - start_idx == idx
            and (
                not is_top
                or (is_top and target_idx >= 4 and target_idx - start_idx == idx)
            )
        ):
            target_row = Image.open("./assets/target_row.png").convert("RGBA")
            img_pos = data["img_position"]
            alpha_mask = target_row.getchannel("A")
            final_img.paste(target_row, (img_pos[0] + 150, img_pos[1]), alpha_mask)
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
    time_range: Optional[str] = "Tất cả", member_id: Optional[int] = None
) -> LeaderboardInfo:
    # TODO: leaderboard real time
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
    elif time_range == "Tháng trước":
        month_start = time_module.first_day_of_last_month()
        month_end = time_module.last_day_of_last_month()
        content = f"Leaderboard tháng {month_start.month}/{month_start.year}"
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
    start_idx = 0
    if member_id:
        try:
            target_idx = next(
                i for i, item in enumerate(results) if item["_id"] == member_id
            )
        except StopIteration:
            raise ValueError("No data")
        start_idx = target_idx // 10 * 10
        end_idx = min([len(results) - 1, start_idx + 10])
        results = results[start_idx:end_idx]
        img_name = f"page-{start_idx//10+1}-" + img_name
    else:
        img_name = "page-1-" + img_name

    users = await asyncio.gather(
        *[Users.find_one({Users.discord_id: result["_id"]}) for result in results]
    )
    users_avatar = await asyncio.gather(
        *[
            save_image(
                user.avatar,
                target_path=f"./assets/cache/{user.discord_id}.png",
                use_cache=True,
            )
            for user in users
        ]
    )

    for idx, result in enumerate(results):
        if start_idx == 0:
            data_info = copy.deepcopy(data_format_infos_top[idx])
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
        result["img"] = (
            users_avatar[idx] if users_avatar[idx] else "./assets/default_avatar.png"
        )
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
                users[idx].name,
                data_info["text_font_size"],
                data_info["text_max_width"],
            )
        else:
            result["text_position"] = data_info["text_position"]
            result["text"] = users[idx].nick if users[idx].nick else users[idx].name
        result["text_font_size"] = data_info["text_font_size"]

        if data_info.get("idx_text_position"):
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
        leaderboard_data=results,
        start_idx=start_idx,
        target_idx=target_idx,
        img_path=img_path,
    )

    return LeaderboardInfo(
        content=content,
        img_path=img_path,
        member_ids=[user.discord_id for user in users],
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
async def leaderboard(
    interaction: discord.Interaction, time_range: app_commands.Choice[int]
):
    await interaction.response.defer()
    # BUG: last one in list
    try:
        leaderboard_info = await generate_leaderboard_info(
            time_range.name, member_id=interaction.user.id
        )
        with open(leaderboard_info.img_path, "rb") as f:
            await interaction.followup.send(
                content=leaderboard_info.content, file=discord.File(f)
            )
    except ValueError:
        await interaction.followup.send(
            content="Bạn chưa học trong khoảng thời gian này"
        )
