import datetime, pytz


def vn_now() -> datetime.datetime:
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    pst_now = utc_now.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
    now = datetime.datetime(
        pst_now.year, pst_now.month, pst_now.day, pst_now.hour, pst_now.minute
    )

    return now


def time_to_str(t: datetime.datetime) -> str:
    return t.strftime("%Y/%m/%d %H:%M:%S")


def str_to_time(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y/%m/%d %H:%M:%S")
