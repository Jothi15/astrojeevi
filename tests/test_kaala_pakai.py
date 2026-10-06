from app.astrology import ChartData, GrahaPosition
from app.constants import GRAHA_NAMES
from app.kaala_pakai import compute_kaala_pakai

# The user's table: graha -> its Kaala Pakai rasis (0=Aries..11=Pisces).
TABLE = {
    "Moon": {0, 1},
    "Rahu": {2},
    "Sun": {3},
    "Mars": {5},
    "Jupiter": {6, 7},
    "Mercury": {8},
    "Venus": {9, 10},
    "Saturn": {11},
    "Ketu": set(),
}


def _chart(lagna_rasi: int, rasis: dict[str, int]) -> ChartData:
    def graha(name, rasi):
        house = ((rasi - lagna_rasi) % 12) + 1
        return GrahaPosition(name, rasi * 30 + 5, rasi, house, 0, 1, 5.0, "", "", False, False)

    return ChartData(lagna_rasi=lagna_rasi, grahas={name: graha(name, rasi) for name, rasi in rasis.items()})


def test_every_graha_in_every_rasi_matches_the_table():
    for name in GRAHA_NAMES:
        for rasi in range(12):
            flagged = compute_kaala_pakai(_chart(0, {name: rasi}))
            assert bool(flagged) == (rasi in TABLE[name]), (name, rasi)


def test_ketu_and_leo_are_never_kaala_pakai():
    for rasi in range(12):
        assert compute_kaala_pakai(_chart(0, {"Ketu": rasi})) == []
    assert compute_kaala_pakai(_chart(0, {name: 4 for name in GRAHA_NAMES})) == []


def test_entry_gives_rasi_and_house_from_lagna():
    [entry] = compute_kaala_pakai(_chart(8, {"Moon": 1, "Sun": 8}))  # Sagittarius lagna, Moon in Taurus
    assert (entry.planet, entry.rasi, entry.house) == ("Moon", 1, 6)


def test_several_grahas_listed_in_chart_order():
    chart = _chart(0, {"Sun": 3, "Moon": 0, "Mars": 0, "Venus": 10})
    assert [e.planet for e in compute_kaala_pakai(chart)] == ["Sun", "Moon", "Venus"]
