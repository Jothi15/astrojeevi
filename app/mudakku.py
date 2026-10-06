from dataclasses import dataclass

from app.astrology import ChartData, nakshatra_lord
from app.constants import RASI_LORDS

MOOLAM = 18  # nakshatra index, Ashwini=0
PADAS_PER_RASI = 9


@dataclass
class MudakkuInfo:
    sun_nakshatra: int
    sun_pada: int
    count: int  # padas from the Sun's pada to the same pada of Moolam, both counted
    nakshatra: int
    pada: int
    star_lord: str
    rasi: int
    rasi_lord: str
    house: int
    planets: list[str]
    is_lagna: bool


def mudakku_point(sun_nakshatra: int, sun_pada: int) -> tuple[int, int, int]:
    """Count padas from the Sun's pada to the same pada of Moolam (both inclusive),
    then the same count again from that Moolam pada (it = 1).
    Returns (count, landing nakshatra, landing pada 1..4)."""
    stars_to_moolam = (MOOLAM - sun_nakshatra) % 27
    count = 4 * stars_to_moolam + 1
    return count, (MOOLAM + stars_to_moolam) % 27, sun_pada


def pada_rasi(nakshatra: int, pada: int) -> int:
    """A pada is 3deg20', nine to a rasi, so it never spans two signs."""
    return (nakshatra * 4 + pada - 1) // PADAS_PER_RASI


def compute_mudakku(chart: ChartData) -> MudakkuInfo:
    sun = chart.grahas["Sun"]
    count, nak, pada = mudakku_point(sun.nakshatra, sun.pada)
    rasi = pada_rasi(nak, pada)
    return MudakkuInfo(
        sun_nakshatra=sun.nakshatra,
        sun_pada=sun.pada,
        count=count,
        nakshatra=nak,
        pada=pada,
        star_lord=nakshatra_lord(nak),
        rasi=rasi,
        rasi_lord=RASI_LORDS[rasi],
        house=((rasi - chart.lagna_rasi) % 12) + 1,
        planets=[name for name, g in chart.grahas.items() if g.rasi == rasi],
        is_lagna=rasi == chart.lagna_rasi,
    )
