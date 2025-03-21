import datetime
import pytz
from typing import Optional
from cachetools.func import ttl_cache


@ttl_cache(maxsize=1, ttl=60)
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

    def first_day_of_month(self) -> datetime.datetime:
        """
        The first day of current month.
        """
        return datetime.datetime(self.now.year, self.now.month, 1)

    def last_day_of_month(self) -> datetime.datetime:
        """
        The last day of current month.
        """
        if self.now.month == 12:
            next_month = 1
            next_year = self.now.year + 1
        else:
            next_month = self.now.month + 1
            next_year = self.now.year

        first_day_next_month = datetime.datetime(next_year, next_month, 1)
        return first_day_next_month - datetime.timedelta(days=1)

    def first_day_of_week(self):
        """
        The first day of current week (Monday).
        """
        weekday = self.today.weekday()  # Monday is 0, Sunday is 6
        days_to_subtract = weekday  # Subtract 'weekday' days to get to Monday
        first_day = self.today - datetime.timedelta(days=days_to_subtract)
        return first_day

    def last_day_of_week(self):
        """
        The last day of current week (Sunday).
        """
        first_day = self.first_day_of_week()  # Get the Monday of the week
        last_day = first_day + datetime.timedelta(days=6)  # Add 6 days to get to Sunday
        return last_day

    def first_day_of_next_month(self) -> datetime.datetime:
        """
        The first day of next month.
        """
        return self.last_day_of_month() + datetime.timedelta(days=1)


def generate_date_strings(
    start_date: datetime.datetime, end_date: datetime.datetime, format_type: Optional[str] = "%d/%m"
) -> datetime.datetime:
    """
    Generate a list of string from date to date with custom format
    """
    date_strings = []
    current_dt = start_date

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    while current_dt <= end_date:
        date_strings.append(current_dt.strftime(format_type))
        current_dt += datetime.timedelta(days=1)
    return date_strings
