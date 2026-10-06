from dataclasses import dataclass, field

from app.astrology import ChartData
from app.constants import RASI_LORDS, THITHI_SOONYA_RASIS

TITHI_SPAN = 12.0  # degrees of Moon-minus-Sun elongation per tithi


@dataclass
class SoonyaRasi:
    rasi: int
    lord: str
    house: int
    planets: list[str]


@dataclass
class TithiInfo:
    number: int  # 1..30 (1-15 Shukla, 16-30 Krishna)
    paksha: str  # "shukla" (waxing) or "krishna" (waning)
    paksha_tithi: int  # 1..15 within the paksha; 15 is Pournami (shukla) or Amavasai (krishna)
    progress: float  # fraction of the tithi elapsed at birth, 0..1
    soonya_rasis: list[SoonyaRasi] = field(default_factory=list)


def tithi_from_longitudes(sun_longitude: float, moon_longitude: float) -> tuple[int, float]:
    """Tithi number 1..30 and how far through it (0..1) from the Moon's lead over the Sun."""
    elongation = (moon_longitude - sun_longitude) % 360
    return int(elongation // TITHI_SPAN) + 1, (elongation % TITHI_SPAN) / TITHI_SPAN


def compute_tithi(chart: ChartData) -> TithiInfo:
    """Birth tithi and its Thithi Soonyam rasis, placed in the D1 chart (whole-sign houses)."""
    number, progress = tithi_from_longitudes(chart.grahas["Sun"].longitude, chart.grahas["Moon"].longitude)
    paksha = "shukla" if number <= 15 else "krishna"
    paksha_tithi = number if number <= 15 else number - 15
    soonya = []
    for rasi in THITHI_SOONYA_RASIS.get(paksha_tithi, ()):
        house = ((rasi - chart.lagna_rasi) % 12) + 1
        planets = [name for name, g in chart.grahas.items() if g.rasi == rasi]
        soonya.append(SoonyaRasi(rasi, RASI_LORDS[rasi], house, planets))
    return TithiInfo(number, paksha, paksha_tithi, progress, soonya)
