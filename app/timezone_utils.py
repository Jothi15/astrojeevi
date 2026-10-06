from datetime import date, datetime, time
from zoneinfo import ZoneInfo


def compute_utc_offset(tz_name: str, dob: date, tob: time) -> float:
    """Historical UTC offset (handles DST rules as they stood on that date) for a
    local birth date/time in the given IANA timezone."""
    local_dt = datetime.combine(dob, tob, tzinfo=ZoneInfo(tz_name))
    return local_dt.utcoffset().total_seconds() / 3600
