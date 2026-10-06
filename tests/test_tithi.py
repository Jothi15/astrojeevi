from app.astrology import ChartData, GrahaPosition
from app.constants import THITHI_SOONYA_RASIS
from app.tithi import compute_tithi, tithi_from_longitudes


def _graha(name: str, longitude: float, lagna_rasi: int) -> GrahaPosition:
    rasi = int(longitude // 30)
    return GrahaPosition(
        name, longitude, rasi, ((rasi - lagna_rasi) % 12) + 1, 0, 1, longitude % 30, "", "", False, False
    )


def _chart(sun: float, moon: float, lagna_rasi: int = 0) -> ChartData:
    return ChartData(
        lagna_rasi=lagna_rasi,
        grahas={"Sun": _graha("Sun", sun, lagna_rasi), "Moon": _graha("Moon", moon, lagna_rasi)},
    )


def test_tithi_boundaries():
    assert tithi_from_longitudes(100.0, 100.0)[0] == 1  # new moon instant starts Prathamai
    assert tithi_from_longitudes(100.0, 111.99)[0] == 1
    assert tithi_from_longitudes(100.0, 112.0)[0] == 2
    assert tithi_from_longitudes(0.0, 179.99)[0] == 15  # Pournami
    assert tithi_from_longitudes(0.0, 180.0)[0] == 16  # Krishna Prathamai
    assert tithi_from_longitudes(0.0, 359.99)[0] == 30  # Amavasai


def test_tithi_wraps_when_moon_longitude_is_below_sun():
    number, progress = tithi_from_longitudes(350.0, 20.0)  # Moon 30 deg ahead across 0 Aries
    assert number == 3
    assert abs(progress - 0.5) < 1e-9


def test_krishna_paksha_uses_same_table():
    t = compute_tithi(_chart(0.0, 180.0 + 12 * 12 + 1))  # tithi 28 = Krishna Trayodasi
    assert (t.number, t.paksha, t.paksha_tithi) == (28, "krishna", 13)
    assert [r.rasi for r in t.soonya_rasis] == [1, 4]  # Taurus, Leo


def test_pournami_and_amavasai_have_no_soonya_rasis():
    assert compute_tithi(_chart(0.0, 175.0)).soonya_rasis == []
    assert compute_tithi(_chart(0.0, 355.0)).soonya_rasis == []


def test_table_pattern_matches_sources():
    # Most pairs are 4th/10th apart; Tritiyai and Saptami 6/8; Shashti 5/9; Chaturdasi all dual signs.
    for tithi, rasis in THITHI_SOONYA_RASIS.items():
        if tithi == 14:
            assert set(rasis) == {2, 5, 8, 11}
            continue
        a, b = rasis
        gap = (b - a) % 12
        expected = {3: {5, 7}, 7: {5, 7}, 6: {4, 8}}.get(tithi, {3, 9})
        assert gap in expected, tithi


def test_soonya_rasi_house_lord_and_planets():
    # Lagna Sagittarius; Moon in Taurus -> Taurus is the 6th house, lord Venus.
    t = compute_tithi(_chart(245.59, 35.76, lagna_rasi=8))
    assert t.paksha_tithi == 13
    taurus, leo = t.soonya_rasis
    assert (taurus.rasi, taurus.lord, taurus.house, taurus.planets) == (1, "Venus", 6, ["Moon"])
    assert (leo.rasi, leo.lord, leo.house, leo.planets) == (4, "Sun", 9, [])
