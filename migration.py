import asyncio
from core.models import UserDailyStudyTime, UserDailyStudyTimes, connect_db


async def run():
    await connect_db()

    # for a in await UserDailyStudyTimes.find().to_list():
    #     await a.delete()

    user_daily_old = await UserDailyStudyTime.find({}, fetch_links=True).to_list()
    user_daily_new = []
    count = 0
    for data in user_daily_old:
        count += 1
        if count % 1000 == 0:
            print(count)
        user_daily_new.append(
            UserDailyStudyTimes(
                user_discord_id=int(data.user.discord_id),
                study_time=data.study_time,
                date=data.date,
            )
        )
    print("Prepare data done")
    command_ok = input('Type "ok" to start change: ')
    if command_ok == "ok":
        print("Begin live changing")
        await UserDailyStudyTimes.insert_many(user_daily_new)
        print("Changing done")


asyncio.run(run())
