from dataclasses import dataclass

from app.astrology import ChartData
from app.constants import PANCHA_MAHAPURUSHA

MANGAL_HOUSES = {1, 2, 4, 7, 8, 12}
KENDRA_OFFSETS = {0, 3, 6, 9}
KENDRA_HOUSES = {1, 4, 7, 10}


@dataclass
class YogaResult:
    name: str
    description: str
    triggered: bool
    from_moon: bool = False  # only set for a yoga that fails from Lagna but holds counting from the Moon


def _has_dignity(planet: str, rasi: int) -> bool:
    _, own_signs, exaltation = PANCHA_MAHAPURUSHA[planet]
    return rasi in own_signs or rasi == exaltation


def detect_pancha_mahapurusha(chart: ChartData) -> list[YogaResult]:
    moon_rasi = chart.grahas["Moon"].rasi
    results = []
    for planet, (name, _own, _exalt) in PANCHA_MAHAPURUSHA.items():
        graha = chart.grahas[planet]
        dignified = _has_dignity(planet, graha.rasi)
        from_lagna = dignified and graha.house in KENDRA_HOUSES
        from_moon = dignified and (((graha.rasi - moon_rasi) % 12) + 1) in KENDRA_HOUSES
        results.append(
            YogaResult(
                name,
                f"{planet} in its own or exaltation sign and in a kendra (1/4/7/10) from Lagna. "
                "Full effect also assumes the planet is not combust or badly afflicted (not modeled).",
                from_lagna,
                from_moon=from_moon and not from_lagna,
            )
        )
    return results


def check_mangal_dosha(chart: ChartData) -> bool:
    return chart.grahas["Mars"].house in MANGAL_HOUSES


def check_gaja_kesari_yoga(chart: ChartData) -> bool:
    moon_rasi = chart.grahas["Moon"].rasi
    jupiter_rasi = chart.grahas["Jupiter"].rasi
    return ((jupiter_rasi - moon_rasi) % 12) in KENDRA_OFFSETS


def check_budhaditya_yoga(chart: ChartData) -> bool:
    return chart.grahas["Sun"].rasi == chart.grahas["Mercury"].rasi


def check_chandra_mangal_yoga(chart: ChartData) -> bool:
    return chart.grahas["Moon"].rasi == chart.grahas["Mars"].rasi


def check_kemadruma_yoga(chart: ChartData) -> bool:
    moon_rasi = chart.grahas["Moon"].rasi
    second_house = ((moon_rasi + 1 - chart.lagna_rasi) % 12) + 1
    twelfth_house = ((moon_rasi - 1 - chart.lagna_rasi) % 12) + 1
    for name, graha in chart.grahas.items():
        if name == "Moon":
            continue
        if graha.house in (second_house, twelfth_house):
            return False
        if graha.rasi == moon_rasi:
            return False
    return True


def check_soorya_chandraadhi_yoga(chart: ChartData) -> bool:
    """The Sun's house from lagna (lagna = 1), counted that many rasis from Mesha
    (Mesha = 1), must be the Moon's rasi. D1 only."""
    return chart.grahas["Moon"].rasi == chart.grahas["Sun"].house - 1


def jeevanam_house(chart: ChartData) -> int:
    """The Moon's rasi numbered from Mesha (Mesha = 1), used as a house count from the lagna."""
    return chart.grahas["Moon"].rasi + 1


def check_jeevanam_yoga(chart: ChartData) -> bool:
    """Any of the nine grahas, the Moon included, in that house. With a Mesha lagna the
    house is the Moon's own rasi, so the yoga is always present. D1 only."""
    return bool(chart.houses[jeevanam_house(chart)])


YOGA_CHECKS = [
    ("Mangal Dosha", "Mars in a dosha house (1,2,4,7,8,12) from lagna. Classical cancellation rules not modeled.", check_mangal_dosha),
    ("Gaja Kesari Yoga", "Jupiter in a kendra from the Moon.", check_gaja_kesari_yoga),
    ("Budhaditya Yoga", "Sun and Mercury share a rasi.", check_budhaditya_yoga),
    ("Chandra-Mangal Yoga", "Moon and Mars share a rasi.", check_chandra_mangal_yoga),
    ("Kemadruma Yoga (simplified)", "No planet in 2nd/12th from Moon or conjunct Moon's rasi. Classical cancellation conditions not modeled.", check_kemadruma_yoga),
    ("Soorya Chandraadhi Yoga", "Count the Sun's house from the lagna, then count that many rasis from Mesha; the Moon is in that rasi.", check_soorya_chandraadhi_yoga),
    ("Jeevanam Yoga", "Number the Moon's rasi from Mesha, then count that many houses from the lagna; one or more planets are in that house. They show how the native earns.", check_jeevanam_yoga),
]


def detect_all_yogas(chart: ChartData) -> list[YogaResult]:
    basic = [YogaResult(name, desc, fn(chart)) for name, desc, fn in YOGA_CHECKS]
    return basic + detect_pancha_mahapurusha(chart)
