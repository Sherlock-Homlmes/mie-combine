import datetime
import pytz


def vn_now() -> datetime.datetime:
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    pst_now = utc_now.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
    now = datetime.datetime(pst_now.year, pst_now.month, pst_now.day, pst_now.hour, pst_now.minute)
    return now


def time_to_str(t: datetime.datetime) -> str:
    return t.strftime("%Y/%m/%d %H:%M:%S")


def str_to_time(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y/%m/%d %H:%M:%S")


class Now:
    def __init__(self):
        now: datetime.datetime = vn_now()
        self.now: datetime.datetime = now
        self.today: datetime.datetime = datetime.datetime(now.year, now.month, now.day)

    def some_day_before(self, days: int) -> datetime.datetime:
        that_day = self.now - datetime.timedelta(days=days)
        return datetime.datetime(that_day.year, that_day.month, that_day.day)

    def some_day_after(self, days: int) -> datetime.datetime:
        that_day = self.now + datetime.timedelta(days=days)
        return datetime.datetime(that_day.year, that_day.month, that_day.day)
