from dataclasses import dataclass

from app.astrology import ChartData

# Whose position the Upasana rasi is counted from: Jupiter for a man, Venus for a woman.
UPASANA_PLANET = {"Male": "Jupiter", "Female": "Venus"}


@dataclass
class UpasanaInfo:
    planet: str
    planet_rasi: int
    rasi: int  # the 11th rasi from the planet, counting the planet's own rasi as 1st


def compute_upasana(chart: ChartData, gender: str) -> UpasanaInfo | None:
    planet = UPASANA_PLANET.get(gender)
    if planet is None:
        return None
    planet_rasi = chart.grahas[planet].rasi
    return UpasanaInfo(planet, planet_rasi, (planet_rasi + 10) % 12)
