# default
import datetime

# lib
from beanie import Document, Link, before_event, Delete

# local
from .users import Users
from other_modules.time_modules import Now
from .user_daily_study_time import UserDailyStudyTime


class UserStudySection(Document):
    user: Link[Users]
    start_study_time: datetime.datetime

    async def update_user_study_time(self):
        now = Now()

        # calculate if start study date = end study date
        if now.now.date() == self.start_study_time.date():
            study_time = timedelta_to_daily_list(self.start_study_time, now.now)

            # if study time != 0
            if any(study_time):
                user_daily_study_time = await UserDailyStudyTime.find_one(
                    UserDailyStudyTime.user.discord_id == self.user.discord_id,
                    UserDailyStudyTime.date == now.today,
                    fetch_links=True,
                )
                if user_daily_study_time:
                    user_daily_study_time.study_time = [
                        (user_daily_study_time.study_time[index] + value)
                        for index, value in enumerate(study_time)
                    ]
                    await user_daily_study_time.save()
                else:
                    await UserDailyStudyTime(
                        user=self.user, study_time=study_time, date=now.today
                    ).insert()

        # calculate if start study date != end study date
        else:
            """
            Start day study time = midnight - start time
            End day study time = end time - midnight
            """
            yesterday_midnight = Now().some_day_before(0)
            yesterday_study_time = timedelta_to_daily_list(
                self.start_study_time, yesterday_midnight
            )
            today_study_time = timedelta_to_daily_list(yesterday_midnight, now.now)

            if any(yesterday_study_time):
                user_daily_study_time = await UserDailyStudyTime.find_one(
                    UserDailyStudyTime.user.discord_id == self.user.discord_id,
                    fetch_links=True,
                )
                if user_daily_study_time:
                    user_daily_study_time.study_time = [
                        (user_daily_study_time.study_time[index] + value)
                        for index, value in enumerate(yesterday_study_time)
                    ]
                    await user_daily_study_time.save()
                else:
                    await UserDailyStudyTime(
                        user=self.user,
                        study_time=yesterday_study_time,
                        date=now.some_day_before(1),
                    ).insert()
                await UserDailyStudyTime(
                    user=self.user, study_time=today_study_time, date=now.today
                ).insert()

    @before_event(Delete)
    async def update_before_delete(self):
        await self.update_user_study_time()


def timedelta_to_daily_list(time1: datetime.datetime, time2: datetime.datetime):
    time2_hour = time2.hour
    if time2.hour != time1.hour or time1.day != time2.day:
        if time2.hour == 0:
            time2_hour = 24
        study_time = [
            (lambda x: 60 if (x > time1.hour and x < time2_hour) else 0)(x) for x in range(0, 24)
        ]
        if time2_hour != 24:
            study_time[time2.hour] = time2.minute
        if not study_time[time1.hour]:
            study_time[time1.hour] = 60 - time1.minute
    elif time1.hour == time2.hour:
        study_time = [0] * 24
        study_time[time2_hour] = time2.minute - time1.minute
    return study_time
