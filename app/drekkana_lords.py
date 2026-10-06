"""Drekkana Lords: whether each planet's drekkana lord (its controller) sits 6th or 8th from it.

The rule and its degree boundaries are the user's own, not classical. A planet at up to
10deg in its rasi is in the 1st drekkana, ruled by its rasi lord; over 10deg up to 20deg,
the 2nd, ruled by the lord of the 5th rasi from it; over 20deg, the 3rd, the 9th rasi's
lord. Degrees are taken to the hundredth, so 10.00 is the 1st and 10.01 the 2nd.
If that controller is in the 6th or 8th rasi from the planet, the planet cannot perform well.
"""

from dataclasses import dataclass

from app.astrology import ChartData
from app.constants import RASI_LORDS

# All nine are checked; Rahu and Ketu rule no rasi, so they are never a controller.
CHECKED_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
DREKKANA_OFFSET = {1: 0, 2: 4, 3: 8}  # the 1st, 5th and 9th rasi from the planet
WEAK_COUNTS = {6, 8}


@dataclass
class DrekkanaLordEntry:
    planet: str
    rasi: int
    degree_in_sign: float
    drekkana: int  # 1, 2 or 3
    drekkana_rasi: int
    controller: str
    controller_rasi: int
    count: int  # the controller's rasi counted from the planet's, planet's rasi = 1
    weakened: bool


def drekkana_number(degree_in_sign: float) -> int:
    degree = round(degree_in_sign, 2)
    return 1 if degree <= 10 else 2 if degree <= 20 else 3


def compute_drekkana_lords(chart: ChartData) -> list[DrekkanaLordEntry]:
    entries = []
    for name in CHECKED_PLANETS:
        g = chart.grahas[name]
        drekkana = drekkana_number(g.degree_in_sign)
        drekkana_rasi = (g.rasi + DREKKANA_OFFSET[drekkana]) % 12
        controller = RASI_LORDS[drekkana_rasi]
        controller_rasi = chart.grahas[controller].rasi
        count = (controller_rasi - g.rasi) % 12 + 1
        entries.append(
            DrekkanaLordEntry(
                planet=name,
                rasi=g.rasi,
                degree_in_sign=g.degree_in_sign,
                drekkana=drekkana,
                drekkana_rasi=drekkana_rasi,
                controller=controller,
                controller_rasi=controller_rasi,
                count=count,
                weakened=count in WEAK_COUNTS,
            )
        )
    return entries
