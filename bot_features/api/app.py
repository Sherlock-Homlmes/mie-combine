# web
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(docs_url="/all-api", redoc_url=None)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# bot
from base import (
    #neccess
    discord, bot, get,
    #var
    guild_id
)
from bot_features.schedule.static_channels import member_info

# var
gender_dict = {
    '891914368789389322': 'Nam',
    '891914526012899370': 'Nữ',
    '891918559016542238': 'Giới tính khác'
}
age_range_dict = {
    '891914202388791316': 'Cấp 2',
    '891914256998600714': 'Cấp 3',
    '891914308903125052': 'Đại học-cao đẳng',
    '915941689774977034': 'Tốt nghiệp-đi làm',
    '915941907534856203': 'Thạc sĩ-Tiến sĩ',    
}


@app.get("/")
async def home():
    return "Hello I'm alive"

@app.get("/member/{member_id}")
async def member(member_id: int):
    member: discord.Member

    member = get(bot.get_all_members(), id= member_id)

    if member:

        gender = None
        age_range = None
        for role in member.roles:
            role_id = str(role.id)

            # gender
            if role_id in gender_dict.keys():
                gender = gender_dict[role_id]

            # age_range
            if role_id in age_range_dict.keys():
                age_range = age_range_dict[role_id]
        
        joined_at = (
            # int(member.joined_at.date), 
            int(member.joined_at.year), int(member.joined_at.month), int(member.joined_at.day), 
            int(member.joined_at.hour), int(member.joined_at.minute), int(member.joined_at.second)
            )
        member_info = {
            "name": member.name,
            "nick": member.nick,
            "discriminator": member.discriminator,
            "avatar_url": member.avatar.url,
            "joined_at": joined_at,
            "gender": gender,
            "age_range": age_range
        }
        print(member_info)
        return JSONResponse(member_info)

    return JSONResponse({"message": "Member not found"})

@app.get("/server-info")
async def server_info():

    mem = member_info()
    data = {
        "total_member": mem[0],
        "online_member": mem[1],
        "study_hour": 1
    }

    return JSONResponse(data)
