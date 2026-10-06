import os
from datetime import date, datetime, time, timedelta, timezone

import swisseph as swe

from app.constants import EPHEMERIS_FLAGS, NODE_MODE

DEFAULT_EPHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ephe")

BODIES = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": NODE_MODE,
}


def init_ephemeris(ephe_path: str | None = None) -> None:
    path = os.path.abspath(ephe_path if ephe_path is not None else DEFAULT_EPHE_PATH)
    swe.set_ephe_path(path)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


def to_julian_day_ut(birth_date: date, birth_time: time, utc_offset_hours: float) -> float:
    local_dt = datetime.combine(birth_date, birth_time)
    utc_dt = local_dt - timedelta(hours=utc_offset_hours)
    hour_decimal = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal, swe.GREG_CAL)


def compute_graha_positions(jd_ut: float) -> dict[str, tuple[float, float]]:
    """Returns {name: (longitude, speed_deg_per_day)}. Negative speed = retrograde."""
    result = {}
    for name, body in BODIES.items():
        xx, _ = swe.calc_ut(jd_ut, body, EPHEMERIS_FLAGS)
        result[name] = (xx[0] % 360, xx[3])
    rahu_lon, rahu_speed = result["Rahu"]
    result["Ketu"] = ((rahu_lon + 180.0) % 360, rahu_speed)  # Ketu mirrors Rahu's motion
    return result


def compute_graha_longitudes(jd_ut: float) -> dict[str, float]:
    return {name: lon for name, (lon, _speed) in compute_graha_positions(jd_ut).items()}


def compute_ascendant(jd_ut: float, lat: float, lon: float) -> float:
    _, ascmc = swe.houses_ex(jd_ut, lat, lon, b"W", EPHEMERIS_FLAGS)
    return ascmc[0] % 360


def jd_from_datetime(dt: datetime) -> float:
    """Julian day (UT) of a time-zone-aware datetime."""
    dt = dt.astimezone(timezone.utc)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60 + dt.second / 3600)


def datetime_from_jd(jd_ut: float) -> datetime:
    y, m, d, h = swe.revjul(jd_ut)
    return datetime(y, m, d, tzinfo=timezone.utc) + timedelta(seconds=round(h * 3600))
