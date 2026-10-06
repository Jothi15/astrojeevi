from datetime import date, time

import swisseph as swe

from app.constants import SATURN_DAY_SEGMENT, SATURN_NIGHT_SEGMENT


def sun_rise_or_set(jd_search_start: float, geopos: tuple, rise: bool) -> float:
    flags = swe.FLG_SWIEPH
    event = swe.CALC_RISE if rise else swe.CALC_SET
    _, tret = swe.rise_trans(jd_search_start, swe.SUN, event, geopos, 0, 0, flags)
    return tret[0]


def _saturn_segment_bounds(dob: date, tob: time, utc_offset: float, lat: float, lon: float) -> tuple[float, float]:
    """Julian-day (start, end) of Saturn's 1/8 segment of the day (sunrise-sunset)
    or night (sunset-sunrise) containing the birth, per the weekday tables in
    app.constants. Shared by Gulika (segment start) and Mandi (segment middle) —
    both are cast from this same segment, differing only in where within it."""
    geopos = (lon, lat, 0)
    jd_local_midnight = swe.julday(dob.year, dob.month, dob.day, 0.0, swe.GREG_CAL) - utc_offset / 24.0

    jd_sunrise = sun_rise_or_set(jd_local_midnight, geopos, rise=True)
    jd_sunset = sun_rise_or_set(jd_local_midnight, geopos, rise=False)
    jd_birth = swe.julday(
        dob.year, dob.month, dob.day,
        tob.hour + tob.minute / 60 + tob.second / 3600 - utc_offset,
        swe.GREG_CAL,
    )

    # Simplification: uses the Gregorian calendar weekday of `dob` even for a
    # birth before sunrise (which panchang convention would attribute to the
    # previous day's "night", since the Hindu day starts at sunrise). This only
    # affects births in the pre-sunrise window.
    weekday_sun0 = (dob.weekday() + 1) % 7  # Python: Monday=0 -> convert to Sunday=0

    if jd_sunrise <= jd_birth < jd_sunset:
        segment_number = SATURN_DAY_SEGMENT[weekday_sun0]
        period_start, period_end = jd_sunrise, jd_sunset
    elif jd_birth >= jd_sunset:
        segment_number = SATURN_NIGHT_SEGMENT[weekday_sun0]
        period_start = jd_sunset
        period_end = sun_rise_or_set(jd_sunset, geopos, rise=True)
    else:
        # birth before sunrise: still the previous night, spanning back to yesterday's sunset
        segment_number = SATURN_NIGHT_SEGMENT[weekday_sun0]
        period_end = jd_sunrise
        period_start = sun_rise_or_set(jd_local_midnight - 1, geopos, rise=False)

    segment_length = (period_end - period_start) / 8
    jd_segment_start = period_start + (segment_number - 1) * segment_length
    jd_segment_end = jd_segment_start + segment_length
    return jd_segment_start, jd_segment_end


def _ascendant_at(jd: float, lat: float, lon: float) -> float:
    sid_flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    _, ascmc = swe.houses_ex(jd, lat, lon, b"W", sid_flags)
    return ascmc[0] % 360


def compute_gulika_longitude(dob: date, tob: time, utc_offset: float, lat: float, lon: float) -> float:
    """Gulika: the ascendant rising at the START of Saturn's segment (JHora's
    default convention). See conversation history for sources — Gulika/Mandi
    conventions vary between traditions (start/middle/end of segment)."""
    jd_start, _ = _saturn_segment_bounds(dob, tob, utc_offset, lat, lon)
    return _ascendant_at(jd_start, lat, lon)


def compute_mandi_longitude(dob: date, tob: time, utc_offset: float, lat: float, lon: float) -> float:
    """Mandi: the ascendant rising at the MIDDLE of Saturn's segment (JHora's
    default convention, distinct from Gulika's segment-start). See conversation
    history for sources."""
    jd_start, jd_end = _saturn_segment_bounds(dob, tob, utc_offset, lat, lon)
    return _ascendant_at((jd_start + jd_end) / 2, lat, lon)
