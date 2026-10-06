from datetime import date, time

import swisseph as swe

from app.constants import FIXED_RASIS, MOVABLE_RASIS
from app.upagraha import sun_rise_or_set

DEGREES_PER_HOUR = 300.0  # 150 vighatis/hour, 15 vighatis per sign, 30 degrees per sign


def sun_sign_offset(sun_rasi: int) -> float:
    """BPHS correction by the Sun's sign type: movable +0, dual +120, fixed +240 degrees."""
    if sun_rasi in MOVABLE_RASIS:
        return 0.0
    if sun_rasi in FIXED_RASIS:
        return 240.0
    return 120.0


def pranapada_longitude(sun_longitude: float, ishta_kala_hours: float) -> float:
    """Sun + (ishta kala in vighatis / 15, read as signs) + the sun-sign correction."""
    sun_rasi = int(sun_longitude // 30) % 12
    return (sun_longitude + sun_sign_offset(sun_rasi) + ishta_kala_hours * DEGREES_PER_HOUR) % 360


def ishta_kala_hours(dob: date, tob: time, utc_offset: float, lat: float, lon: float) -> float:
    """Hours since the sunrise that began the birth's day. A birth before that day's
    sunrise counts from the previous day's sunrise (so the value is under 24)."""
    geopos = (lon, lat, 0)
    jd_local_midnight = swe.julday(dob.year, dob.month, dob.day, 0.0, swe.GREG_CAL) - utc_offset / 24.0
    jd_birth = swe.julday(
        dob.year, dob.month, dob.day,
        tob.hour + tob.minute / 60 + tob.second / 3600 - utc_offset,
        swe.GREG_CAL,
    )
    jd_sunrise = sun_rise_or_set(jd_local_midnight, geopos, rise=True)
    if jd_birth < jd_sunrise:
        jd_sunrise = sun_rise_or_set(jd_local_midnight - 1, geopos, rise=True)
    return (jd_birth - jd_sunrise) * 24


def compute_pranapada_longitude(
    dob: date, tob: time, utc_offset: float, lat: float, lon: float, sun_longitude: float
) -> float:
    return pranapada_longitude(sun_longitude, ishta_kala_hours(dob, tob, utc_offset, lat, lon))
