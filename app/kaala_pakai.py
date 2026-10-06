from dataclasses import dataclass

from app.astrology import ChartData
from app.constants import KAALA_PAKAI_RASIS


@dataclass
class KaalaPakaiEntry:
    planet: str
    rasi: int
    house: int


def compute_kaala_pakai(chart: ChartData) -> list[KaalaPakaiEntry]:
    """Grahas sitting in one of their Kaala Pakai rasis in this chart (D1 only)."""
    return [
        KaalaPakaiEntry(name, g.rasi, g.house)
        for name, g in chart.grahas.items()
        if g.rasi in KAALA_PAKAI_RASIS.get(name, ())
    ]
