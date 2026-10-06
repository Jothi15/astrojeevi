from dataclasses import dataclass
from datetime import datetime, timedelta

from app.astrology import NAKSHATRA_SPAN
from app.constants import DASA_ORDER, DASA_YEARS

DAYS_PER_YEAR = 365.25


@dataclass
class DasaPeriod:
    lord: str
    start: datetime
    end: datetime
    level: str


def moon_nakshatra_balance(moon_longitude: float) -> tuple[str, float]:
    nak = int(moon_longitude // NAKSHATRA_SPAN) % 27
    lord = DASA_ORDER[nak % 9]
    fraction_elapsed = (moon_longitude % NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    balance_years = (1 - fraction_elapsed) * DASA_YEARS[lord]
    return lord, balance_years


def compute_mahadasas(birth_dt: datetime, moon_longitude: float, years_to_cover: float = 120) -> list[DasaPeriod]:
    lord, balance = moon_nakshatra_balance(moon_longitude)
    periods: list[DasaPeriod] = []
    start = birth_dt
    idx = DASA_ORDER.index(lord)
    remaining = years_to_cover
    duration = balance
    while remaining > 0:
        current_lord = DASA_ORDER[idx % 9]
        end = start + timedelta(days=duration * DAYS_PER_YEAR)
        periods.append(DasaPeriod(current_lord, start, end, "mahadasa"))
        remaining -= duration
        start = end
        idx += 1
        duration = DASA_YEARS[DASA_ORDER[idx % 9]]
    return periods


def compute_sub_periods(parent_lord: str, parent_start: datetime, parent_end: datetime, level: str) -> list[DasaPeriod]:
    start_idx = DASA_ORDER.index(parent_lord)
    parent_days = (parent_end - parent_start).total_seconds() / 86400
    periods: list[DasaPeriod] = []
    cursor = parent_start
    for i in range(9):
        sub_lord = DASA_ORDER[(start_idx + i) % 9]
        dur_days = parent_days * DASA_YEARS[sub_lord] / 120
        end = cursor + timedelta(days=dur_days)
        periods.append(DasaPeriod(sub_lord, cursor, end, level))
        cursor = end
    return periods
