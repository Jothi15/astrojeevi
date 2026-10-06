from app.astrology import ChartData, GrahaPosition
from app.upasana import compute_upasana


def _chart(jupiter_rasi: int, venus_rasi: int) -> ChartData:
    def graha(name, rasi):
        return GrahaPosition(name, rasi * 30 + 5, rasi, 1, 0, 1, 5.0, "", "", False, False)

    return ChartData(lagna_rasi=0, grahas={"Jupiter": graha("Jupiter", jupiter_rasi), "Venus": graha("Venus", venus_rasi)})


def test_man_counts_from_jupiter():
    u = compute_upasana(_chart(jupiter_rasi=6, venus_rasi=0), "Male")  # Jupiter in Libra
    assert (u.planet, u.planet_rasi, u.rasi) == ("Jupiter", 6, 4)  # 11th from Libra is Leo


def test_woman_counts_from_venus():
    u = compute_upasana(_chart(jupiter_rasi=0, venus_rasi=7), "Female")  # Venus in Scorpio
    assert (u.planet, u.planet_rasi, u.rasi) == ("Venus", 7, 5)  # 11th from Scorpio is Virgo


def test_eleventh_wraps_round_the_zodiac():
    assert compute_upasana(_chart(jupiter_rasi=0, venus_rasi=0), "Male").rasi == 10  # Aries -> Aquarius
    assert compute_upasana(_chart(jupiter_rasi=2, venus_rasi=0), "Male").rasi == 0  # Gemini -> Aries


def test_no_result_for_other_gender():
    assert compute_upasana(_chart(0, 0), "Other") is None
