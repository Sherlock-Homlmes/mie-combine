from discord import Guild

from core.conf.bot.conf import bot, guild_id
from models import VoiceChannels

all_created_vc_id = []
is_ready = False
guild: Guild = None
vc_id_name_map = {}


def find_first_missing_number(lst):
    num_set = set(lst)
    i = 1
    while i in num_set:
        i += 1
    return i


class Room:
    def __init__(self):
        self.number: int | None = None

    def get_new_room_number(self):
        self.number = find_first_missing_number(vc_id_name_map.values())

    def get_room_number_from_room_name(self, room_name: str):
        try:
            self.number = int(room_name.replace("#room ", ""))
        except ValueError:
            self.number = None


# TODO: fix room include remove additional_category_ids
async def fix_room():
    global vc_id_name_map, guild

    all_vc = [x.vc_id for x in await VoiceChannels.find({}).to_list()]
    all_vc.extend(all_created_vc_id)
    all_vc = set(all_vc)

    for vc_id in all_vc:
        vc_channel = guild.get_channel(vc_id)

        if vc_channel:
            if vc_channel.members == []:
                await vc_channel.delete()
                vc = await VoiceChannels.find_one(VoiceChannels.vc_id == vc_id)
                await vc.delete()
            else:
                room = Room()
                room.get_room_number_from_room_name(vc_channel.name)
                if room.number is not None:
                    vc_id_name_map[vc_id] = room.number
        else:
            vc = await VoiceChannels.find_one(VoiceChannels.vc_id == vc_id)
            await vc.delete()

    print("fix voice channel done")


@bot.listen()
async def on_ready():
    global guild, is_ready

    await bot._fully_ready.wait()
    print("6.Create voice channel ready")
    # get all created voice channel
    guild = bot.get_guild(guild_id)
    all_created_vc_id.clear()
    all_created_vc_id.extend(
        [vc.vc_id for vc in await VoiceChannels.find({}).to_list()]
    )

    # delete empty voice channel
    print("out start fixing")
    await fix_room()
    is_ready = True
