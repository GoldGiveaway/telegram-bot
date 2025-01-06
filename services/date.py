from datetime import datetime
import pytz

moscow_tz = pytz.timezone('Europe/Moscow')


def now_datetime() -> datetime:
    return datetime.now(moscow_tz)

def date_to_string(date) -> str:
    return date.strftime('%H:%M %d.%m.%Y')

def string_to_date(date_str) -> datetime:
    return datetime.strptime(date_str, '%H:%M %d.%m.%Y').astimezone(pytz.utc)
