from dataclasses import dataclass

from app.constants import TARA_CATEGORIES, TARA_QUALITY


@dataclass
class TaraEntry:
    nakshatra: int
    count: int
    category: str
    quality: str


def compute_tara_balam(birth_nakshatra: int) -> list[TaraEntry]:
    entries = []
    for nak in range(27):
        count = ((nak - birth_nakshatra) % 27) + 1
        category = TARA_CATEGORIES[(count - 1) % 9]
        entries.append(TaraEntry(nakshatra=nak, count=count, category=category, quality=TARA_QUALITY[category]))
    return entries
