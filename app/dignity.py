from dataclasses import dataclass

from app.astrology import ChartData
from app.constants import DIGNITY


@dataclass
class DignityEntry:
    planet: str
    state: str  # "ucham" (exalted) or "neecham" (debilitated)
    rasi: int
    degree_in_sign: float
    deep_degree: float | None
    degrees_from_deep: float | None


def compute_dignities(chart: ChartData) -> list[DignityEntry]:
    """Planets in their exaltation or debilitation sign (D1, sign-based).
    Neecha Bhanga (cancellation of debilitation) is not modeled."""
    entries = []
    for planet, (exalt_rasi, debil_rasi, deep) in DIGNITY.items():
        graha = chart.grahas[planet]
        if graha.rasi == exalt_rasi:
            state = "ucham"
        elif graha.rasi == debil_rasi:
            state = "neecham"
        else:
            continue
        distance = abs(graha.degree_in_sign - deep) if deep is not None else None
        entries.append(DignityEntry(planet, state, graha.rasi, graha.degree_in_sign, deep, distance))
    return entries
