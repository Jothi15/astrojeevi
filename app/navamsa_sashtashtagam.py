"""Navamsa Sashtashtagam: a planet whose D9 rasi is 6th or 8th from its D1 rasi.

Counted from the planet's D1 rasi (= 1) to its navamsa rasi. None of the nine being 6th or
8th is a big plus; a planet that is brings issues related to it and to the houses it rules
(its aathipathyam) in D1. The rule is the user's own.

For a flagged planet, the issue shows while that same planet, in transit, is in the nakshatra
pada of its natal navamsa position: hours for the Moon, days for the Sun, months for Saturn.
"""

from dataclasses import dataclass, field
from datetime import datetime

import swisseph as swe

from app.astrology import ChartData, house_of_rasi
from app.constants import EPHEMERIS_FLAGS, GRAHA_NAMES, RASI_LORDS
from app.ephemeris import BODIES, datetime_from_jd, jd_from_datetime

SASHTASHTAGAM_COUNTS = {6, 8}
PADA_SPAN = 360 / 108
# Scan steps short enough that no pass through a 3deg20' pada is missed.
SCAN_STEP_DAYS = {"Moon": 1 / 24, "Sun": 0.25, "Mercury": 0.25, "Venus": 0.25, "Mars": 0.5}
DEFAULT_SCAN_STEP_DAYS = 1.0
BISECT_STEPS = 20


@dataclass
class NavamsaPoint:
    nakshatra: int  # Ashwini = 0
    pada: int  # 1..4
    start: float  # sidereal longitude where the pada begins
    end: float


@dataclass
class TransitWindow:
    start: datetime  # UTC
    end: datetime


@dataclass
class SashtashtagamEntry:
    planet: str
    d1_rasi: int
    d1_house: int
    d9_rasi: int
    count: int  # the D9 rasi counted from the D1 rasi, D1 rasi = 1
    flagged: bool
    houses_ruled: list[int]  # D1 houses whose rasi this planet lords; none for Rahu and Ketu
    point: NavamsaPoint | None = None  # only for a flagged planet
    transits: list[TransitWindow] = field(default_factory=list)  # only when a window is asked for


def houses_ruled(planet: str, lagna_rasi: int) -> list[int]:
    return sorted(house_of_rasi(rasi, lagna_rasi) for rasi in range(12) if RASI_LORDS[rasi] == planet)


def navamsa_point(longitude: float) -> NavamsaPoint:
    """The nakshatra pada holding a planet's navamsa longitude (its longitude times 9)."""
    index = int(((longitude * 9) % 360) // PADA_SPAN)
    return NavamsaPoint(index // 4, index % 4 + 1, index * PADA_SPAN, (index + 1) * PADA_SPAN)


def _longitude(planet: str, jd_ut: float) -> float:
    body = BODIES["Rahu" if planet == "Ketu" else planet]
    lon = swe.calc_ut(jd_ut, body, EPHEMERIS_FLAGS)[0][0] % 360
    return (lon + 180) % 360 if planet == "Ketu" else lon


def transit_windows(planet: str, point: NavamsaPoint, start: datetime, end: datetime) -> list[TransitWindow]:
    """Every stretch between start and end when the planet is inside the point's pada.
    A stretch already under way at start begins at start; one still running at end ends at end."""
    inside = lambda jd: point.start <= _longitude(planet, jd) < point.end

    def edge(lo: float, hi: float) -> float:
        # lo and hi straddle an entry or exit; narrow down to the moment it changes.
        was_inside = inside(lo)
        for _ in range(BISECT_STEPS):
            mid = (lo + hi) / 2
            if inside(mid) == was_inside:
                lo = mid
            else:
                hi = mid
        return hi

    step = SCAN_STEP_DAYS.get(planet, DEFAULT_SCAN_STEP_DAYS)
    jd, jd_end = jd_from_datetime(start), jd_from_datetime(end)
    windows = []
    entered = jd if inside(jd) else None
    while jd < jd_end:
        nxt = min(jd + step, jd_end)
        now_inside = inside(nxt)
        if entered is None and now_inside:
            entered = edge(jd, nxt)
        elif entered is not None and not now_inside:
            windows.append(TransitWindow(datetime_from_jd(entered), datetime_from_jd(edge(jd, nxt))))
            entered = None
        jd = nxt
    if entered is not None:
        windows.append(TransitWindow(datetime_from_jd(entered), datetime_from_jd(jd_end)))
    return windows


def compute_navamsa_sashtashtagam(
    d1: ChartData, d9: ChartData, start: datetime | None = None, end: datetime | None = None
) -> list[SashtashtagamEntry]:
    """With start and end, flagged planets also get their transit windows over their point."""
    entries = []
    for name in GRAHA_NAMES:
        g = d1.grahas[name]
        d9_rasi = d9.grahas[name].rasi
        count = (d9_rasi - g.rasi) % 12 + 1
        entries.append(
            SashtashtagamEntry(
                planet=name,
                d1_rasi=g.rasi,
                d1_house=g.house,
                d9_rasi=d9_rasi,
                count=count,
                flagged=count in SASHTASHTAGAM_COUNTS,
                houses_ruled=houses_ruled(name, d1.lagna_rasi),
            )
        )
        entry = entries[-1]
        if entry.flagged:
            entry.point = navamsa_point(g.longitude)
            if start is not None and end is not None:
                entry.transits = transit_windows(name, entry.point, start, end)
    return entries
