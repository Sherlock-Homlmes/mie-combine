# lib
from fastapi import HTTPException
import discord

# local
from .app import app
from other_modules.time_modules import time_to_str
from bot import server_info

# var
gender_dict = {
    "891914368789389322": "Nam",
    "891914526012899370": "Nữ",
    "891918559016542238": "Giới tính khác",
}
age_range_dict = {
    "891914202388791316": "Cấp 2",
    "891914256998600714": "Cấp 3",
    "891914308903125052": "Đại học-cao đẳng",
    "915941689774977034": "Tốt nghiệp-đi làm",
    "915941907534856203": "Thạc sĩ-Tiến sĩ",
}


@app.get("/member/{member_id}")
async def get_a_member(member_id: int):
    member: discord.Member = await server_info.guild.fetch_member(member_id)
    if member:
        gender, age_range = None, None
        for role in member.roles:
            role_id = str(role.id)

            # gender
            if role_id in gender_dict.keys():
                gender = gender_dict[role_id]

            # age_range
            if role_id in age_range_dict.keys():
                age_range = age_range_dict[role_id]

        joined_at = time_to_str(member.joined_at)
        member_info = {
            "name": member.name,
            "nick": member.nick,
            "discriminator": member.discriminator,
            "avatar_url": member.avatar.url,
            "joined_at": joined_at,
            "gender": gender,
            "age_range": age_range,
        }
        return member_info

    raise HTTPException(detail="Member not found", status_code=400)
