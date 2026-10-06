"""Peyarchi (rasi changes) of Saturn, Jupiter and Rahu/Ketu, and the Moorthi of each.

Moorthi Nirnayam: at the moment a planet enters a rasi, count from the janma rasi
(birth Moon) to the rasi the Moon is in, janma rasi = 1. See MOORTHI_BY_COUNT.
"""

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

import swisseph as swe

from app.constants import EPHEMERIS_FLAGS, MOORTHI_BY_COUNT, NODE_MODE
from app.ephemeris import datetime_from_jd, jd_from_datetime

# Ketu is always opposite Rahu, so one Rahu row covers both.
PEYARCHI_BODIES = {"Saturn": swe.SATURN, "Jupiter": swe.JUPITER, "Rahu": NODE_MODE}
# Direction of normal motion through the rasis: +1 forward, -1 backward (the nodes).
NATURAL_DIRECTION = {"Saturn": 1, "Jupiter": 1, "Rahu": -1}
SCAN_STEP_DAYS = 1.0
# Far enough back to find the peyarchi already in effect when the window opens
# (Saturn stays up to about 2.5 years in a rasi, retrograde loops included).
LOOKBACK_DAYS = 3 * 365
BISECT_STEPS = 24  # 1 day / 2**24 is well under a second


@dataclass
class Ingress:
    planet: str
    jd_ut: float
    rasi: int
    kind: str  # "normal", "retrograde" (slips back into the previous rasi) or "re-entry"


@dataclass
class PeyarchiEntry:
    planet: str
    when: datetime  # UTC
    rasi: int
    kind: str
    moon_rasi: int
    count: int
    moorthi: str
    in_effect_at_start: bool  # began before the window but was still running when it opened


def _rasi(jd_ut: float, body: int) -> int:
    xx, _ = swe.calc_ut(jd_ut, body, EPHEMERIS_FLAGS)
    return int((xx[0] % 360) // 30)


@lru_cache(maxsize=32)
def find_ingresses(planet: str, jd_start: float, jd_end: float) -> tuple[Ingress, ...]:
    body = PEYARCHI_BODIES[planet]
    natural = NATURAL_DIRECTION[planet]
    events: list[Ingress] = []
    jd, rasi = jd_start, _rasi(jd_start, body)
    while jd < jd_end:
        step_end = min(jd + SCAN_STEP_DAYS, jd_end)
        new_rasi = _rasi(step_end, body)
        if new_rasi != rasi:
            lo, hi = jd, step_end
            for _ in range(BISECT_STEPS):
                mid = (lo + hi) / 2
                if _rasi(mid, body) == rasi:
                    lo = mid
                else:
                    hi = mid
            direction = 1 if (new_rasi - rasi) % 12 == 1 else -1
            if direction != natural:
                kind = "retrograde"
            elif events and events[-1].kind == "retrograde":
                kind = "re-entry"
            else:
                kind = "normal"
            events.append(Ingress(planet, hi, new_rasi, kind))
            rasi = new_rasi
        jd = step_end
    return tuple(events)


def moorthi_for(janma_rasi: int, moon_rasi: int) -> tuple[int, str]:
    count = (moon_rasi - janma_rasi) % 12 + 1
    return count, MOORTHI_BY_COUNT[count]


def compute_peyarchis(janma_rasi: int, start: datetime, end: datetime) -> list[PeyarchiEntry]:
    """Every peyarchi between start and end, plus the one per planet already in effect at start."""
    jd_start, jd_end = jd_from_datetime(start), jd_from_datetime(end)
    entries = []
    for planet in PEYARCHI_BODIES:
        ingresses = find_ingresses(planet, jd_start - LOOKBACK_DAYS, jd_end)
        earlier = [i for i in ingresses if i.jd_ut < jd_start]
        chosen = earlier[-1:] + [i for i in ingresses if i.jd_ut >= jd_start]
        for ingress in chosen:
            moon_rasi = _rasi(ingress.jd_ut, swe.MOON)
            count, moorthi = moorthi_for(janma_rasi, moon_rasi)
            entries.append(
                PeyarchiEntry(
                    planet=planet,
                    when=datetime_from_jd(ingress.jd_ut),
                    rasi=ingress.rasi,
                    kind=ingress.kind,
                    moon_rasi=moon_rasi,
                    count=count,
                    moorthi=moorthi,
                    in_effect_at_start=ingress.jd_ut < jd_start,
                )
            )
    return sorted(entries, key=lambda e: e.when)
