from dataclasses import dataclass, field

from app.constants import (
    DASA_ORDER,
    DUAL_RASIS,
    FIXED_RASIS,
    GRAHA_NAMES,
    INDU_KALA,
    MOVABLE_RASIS,
    PUSHKARA_NAVAMSA_PARTS,
    RASI_ELEMENTS,
    RASI_LORDS,
)

NAKSHATRA_SPAN = 360 / 27
PADA_SPAN = NAKSHATRA_SPAN / 4


@dataclass
class GrahaPosition:
    name: str
    longitude: float
    rasi: int
    house: int
    nakshatra: int
    pada: int
    degree_in_sign: float
    rasi_lord: str
    star_lord: str
    retrograde: bool
    pushkara_navamsa: bool


@dataclass
class ChartData:
    lagna_rasi: int
    grahas: dict[str, GrahaPosition] = field(default_factory=dict)
    houses: dict[int, list[str]] = field(default_factory=dict)


def longitude_to_rasi(longitude: float) -> int:
    return int(longitude // 30) % 12


def longitude_to_nakshatra_pada(longitude: float) -> tuple[int, int]:
    nak = int(longitude // NAKSHATRA_SPAN) % 27
    within = longitude % NAKSHATRA_SPAN
    pada = int(within // PADA_SPAN) + 1
    return nak, pada


def whole_sign_houses(lagna_rasi: int) -> dict[int, int]:
    return {house: (lagna_rasi + house - 1) % 12 for house in range(1, 13)}


def house_of_rasi(rasi: int, lagna_rasi: int) -> int:
    return ((rasi - lagna_rasi) % 12) + 1


def nakshatra_lord(nak_index: int) -> str:
    return DASA_ORDER[nak_index % 9]


def compute_indu_lagna(lagna_rasi: int, moon_rasi: int) -> int:
    """9th lord from Lagna + 9th lord from Moon, summed by classical Kala
    values, remainder mod 12 (0->12) counted forward from the Moon's sign."""
    ninth_from_lagna = (lagna_rasi + 8) % 12
    ninth_from_moon = (moon_rasi + 8) % 12
    total = INDU_KALA[RASI_LORDS[ninth_from_lagna]] + INDU_KALA[RASI_LORDS[ninth_from_moon]]
    remainder = total % 12 or 12
    return (moon_rasi + remainder - 1) % 12


def make_graha_position(
    name: str, longitude: float, rasi: int, lagna_rasi: int, retrograde: bool = False
) -> GrahaPosition:
    nak, pada = longitude_to_nakshatra_pada(longitude)
    house = house_of_rasi(rasi, lagna_rasi)
    return GrahaPosition(
        name=name,
        longitude=longitude,
        rasi=rasi,
        house=house,
        nakshatra=nak,
        pada=pada,
        degree_in_sign=longitude % 30,
        rasi_lord=RASI_LORDS[rasi],
        star_lord=nakshatra_lord(nak),
        retrograde=retrograde,
        pushkara_navamsa=is_pushkara_navamsa(longitude),
    )


def build_chart(
    lagna_longitude: float, graha_longitudes: dict[str, float], graha_speeds: dict[str, float]
) -> ChartData:
    lagna_rasi = longitude_to_rasi(lagna_longitude)
    houses: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    grahas: dict[str, GrahaPosition] = {}
    for name in GRAHA_NAMES:
        longitude = graha_longitudes[name]
        rasi = longitude_to_rasi(longitude)
        retrograde = graha_speeds[name] < 0
        grahas[name] = make_graha_position(name, longitude, rasi, lagna_rasi, retrograde)
        houses[house_of_rasi(rasi, lagna_rasi)].append(name)
    return ChartData(lagna_rasi=lagna_rasi, grahas=grahas, houses=houses)


# --- Divisional charts (varga) ---
# Each varga has its own classical (Parashari) starting-sign rule; formulas
# are not interchangeable across vargas, so each gets an explicit function.

def _part_index(longitude: float, n: int) -> int:
    return int((longitude % 30) // (30 / n))


def is_pushkara_navamsa(longitude: float) -> bool:
    """2 of the 9 navamsa divisions per sign are especially auspicious
    ('nourishing') — which two depends on the sign's element. See app/constants.py
    for the table and its verification."""
    rasi = longitude_to_rasi(longitude)
    element = RASI_ELEMENTS[rasi]
    part = _part_index(longitude, 9)
    return part in PUSHKARA_NAVAMSA_PARTS[element]


def d2_hora(longitude: float) -> int:
    rasi = longitude_to_rasi(longitude)
    part = _part_index(longitude, 2)
    odd_sign = rasi % 2 == 0  # rasi index 0 = Aries = odd sign (1st)
    if odd_sign:
        return 4 if part == 0 else 3  # Leo : Cancer
    return 3 if part == 0 else 4  # Cancer : Leo


def d3_drekkana(longitude: float) -> int:
    rasi = longitude_to_rasi(longitude)
    part = _part_index(longitude, 3)
    return (rasi + part * 4) % 12


def d7_saptamsa(longitude: float) -> int:
    rasi = longitude_to_rasi(longitude)
    part = _part_index(longitude, 7)
    odd_sign = rasi % 2 == 0
    start = rasi if odd_sign else (rasi + 6) % 12
    return (start + part) % 12


def d9_navamsa(longitude: float) -> int:
    rasi = longitude_to_rasi(longitude)
    part = _part_index(longitude, 9)
    if rasi in MOVABLE_RASIS:
        start = rasi
    elif rasi in FIXED_RASIS:
        start = (rasi + 8) % 12
    else:
        start = (rasi + 4) % 12
    return (start + part) % 12


def d10_dasamsa(longitude: float) -> int:
    rasi = longitude_to_rasi(longitude)
    part = _part_index(longitude, 10)
    odd_sign = rasi % 2 == 0
    start = rasi if odd_sign else (rasi + 8) % 12
    return (start + part) % 12


def d12_dwadasamsa(longitude: float) -> int:
    rasi = longitude_to_rasi(longitude)
    part = _part_index(longitude, 12)
    return (rasi + part) % 12


def d60_shashtiamsa(longitude: float) -> int:
    # Unlike D3/D7/D9/D10, classical BPHS gives no odd/even reversal for D60 —
    # each sign's 60 amsas (0.5deg each) simply count forward from the sign itself.
    rasi = longitude_to_rasi(longitude)
    part = _part_index(longitude, 60)
    return (rasi + part) % 12


VARGA_FUNCTIONS = {
    "D2": d2_hora,
    "D3": d3_drekkana,
    "D7": d7_saptamsa,
    "D9": d9_navamsa,
    "D10": d10_dasamsa,
    "D12": d12_dwadasamsa,
    "D60": d60_shashtiamsa,
}


def build_varga_chart(
    varga: str, lagna_longitude: float, graha_longitudes: dict[str, float], graha_speeds: dict[str, float]
) -> ChartData:
    fn = VARGA_FUNCTIONS[varga]
    lagna_rasi = fn(lagna_longitude)
    houses: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    grahas: dict[str, GrahaPosition] = {}
    for name in GRAHA_NAMES:
        longitude = graha_longitudes[name]
        rasi = fn(longitude)
        retrograde = graha_speeds[name] < 0
        grahas[name] = make_graha_position(name, longitude, rasi, lagna_rasi, retrograde)
        houses[house_of_rasi(rasi, lagna_rasi)].append(name)
    return ChartData(lagna_rasi=lagna_rasi, grahas=grahas, houses=houses)
