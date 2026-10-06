import pytest

from app.astrology import (
    compute_indu_lagna,
    d2_hora,
    d3_drekkana,
    d7_saptamsa,
    d9_navamsa,
    d10_dasamsa,
    d12_dwadasamsa,
    d60_shashtiamsa,
    is_pushkara_navamsa,
    longitude_to_nakshatra_pada,
    longitude_to_rasi,
    make_graha_position,
    nakshatra_lord,
    whole_sign_houses,
)
from app.constants import DASA_ORDER, RASI_LORDS


def test_longitude_to_rasi_boundaries():
    assert longitude_to_rasi(0) == 0
    assert longitude_to_rasi(29.999) == 0
    assert longitude_to_rasi(30) == 1
    assert longitude_to_rasi(359.999) == 11
    assert longitude_to_rasi(360) == 0


def test_nakshatra_pada_boundaries():
    # Ashwini spans 0 - 13.3333..., pada = 3.3333... each
    assert longitude_to_nakshatra_pada(0) == (0, 1)
    assert longitude_to_nakshatra_pada(3.3333) == (0, 1)
    assert longitude_to_nakshatra_pada(3.34) == (0, 2)
    assert longitude_to_nakshatra_pada(13.3333) == (0, 4)
    assert longitude_to_nakshatra_pada(13.34) == (1, 1)


def test_whole_sign_houses_wraparound():
    for lagna in range(12):
        houses = whole_sign_houses(lagna)
        assert houses[1] == lagna
        assert houses[12] == (lagna - 1) % 12
        assert sorted(houses.values()) == list(range(12))


def test_d9_navamsa_aries_zero():
    # 0 deg Aries (movable, starts at self) -> part 0 -> Aries
    assert d9_navamsa(0.0) == 0


def test_d9_navamsa_fixed_sign_starts_at_ninth():
    # Taurus (fixed sign, index 1) starts navamsa count from its 9th sign (index 9, Capricorn).
    # 1 deg into Taurus (longitude 31.0) is part 0 of the 9 navamsa divisions -> Capricorn itself.
    assert d9_navamsa(31.0) == 9


def test_d2_hora_only_cancer_or_leo():
    for lon in [0, 10, 20, 30, 45, 100, 200, 300, 359]:
        assert d2_hora(lon) in (3, 4)


def test_d3_drekkana_trine_scheme():
    assert d3_drekkana(0.0) == 0  # part 0 -> same sign
    assert d3_drekkana(11.0) == 4  # part 1 (10-20deg) -> 5th sign (index 0+4=4)
    assert d3_drekkana(21.0) == 8  # part 2 (20-30deg) -> 9th sign (index 0+8=8)


def test_d7_saptamsa_odd_even_start():
    assert d7_saptamsa(0.0) == 0  # Aries (odd sign) starts at itself
    assert d7_saptamsa(30.0) == 7  # Taurus (even sign) starts at its 7th sign (index 1+6=7, Scorpio)


def test_d10_dasamsa_odd_even_start():
    assert d10_dasamsa(0.0) == 0  # Aries odd sign starts at itself
    assert d10_dasamsa(30.0) == 9  # Taurus even sign starts at its 9th (index1+8=9)


def test_d12_dwadasamsa_uniform():
    assert d12_dwadasamsa(0.0) == 0
    assert d12_dwadasamsa(2.5) == 1
    assert d12_dwadasamsa(30.0) == 1


def test_d60_shashtiamsa_uniform_no_reversal():
    # Each 0.5deg division counts forward from the sign itself, no odd/even flip
    assert d60_shashtiamsa(0.0) == 0  # Aries, part 0 -> Aries
    assert d60_shashtiamsa(0.4) == 0  # still part 0 (< 0.5deg)
    assert d60_shashtiamsa(0.5) == 1  # part 1 -> Taurus
    assert d60_shashtiamsa(29.9) == 11  # last part (59) of Aries -> Pisces
    assert d60_shashtiamsa(30.0) == 1  # Taurus, part 0 -> Taurus itself
    assert d60_shashtiamsa(30.5) == 2  # Taurus, part 1 -> Gemini


def test_d60_shashtiamsa_covers_all_60_parts_per_sign():
    seen_signs = {d60_shashtiamsa(part * 0.5 + 0.01) for part in range(60)}
    assert seen_signs == set(range(12))


def test_nakshatra_lord_cycles_dasa_order():
    for i in range(27):
        assert nakshatra_lord(i) == DASA_ORDER[i % 9]
    # spot checks against known lordships
    assert nakshatra_lord(0) == "Ketu"  # Ashwini
    assert nakshatra_lord(8) == "Mercury"  # Ashlesha, end of first 9-cycle
    assert nakshatra_lord(26) == "Mercury"  # Revati, end of third 9-cycle


def test_rasi_lords_table_shape():
    assert len(RASI_LORDS) == 12
    assert RASI_LORDS[0] == "Mars"  # Aries
    assert RASI_LORDS[3] == "Moon"  # Cancer
    assert RASI_LORDS[4] == "Sun"  # Leo
    assert RASI_LORDS[9] == "Saturn"  # Capricorn
    # every sign is ruled by one of the 7 classical grahas, never Rahu/Ketu
    assert set(RASI_LORDS) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}


def test_make_graha_position_computes_lordships_and_degree_in_sign():
    # 40 deg = 10 deg into Taurus (rasi 1); Taurus lord is Venus
    pos = make_graha_position("Mars", 40.0, longitude_to_rasi(40.0), lagna_rasi=0)
    assert pos.rasi == 1
    assert pos.rasi_lord == "Venus"
    assert abs(pos.degree_in_sign - 10.0) < 1e-9
    assert pos.star_lord == nakshatra_lord(pos.nakshatra)
    assert pos.retrograde is False


def test_make_graha_position_retrograde_flag():
    direct = make_graha_position("Mercury", 40.0, longitude_to_rasi(40.0), lagna_rasi=0, retrograde=False)
    retro = make_graha_position("Mercury", 40.0, longitude_to_rasi(40.0), lagna_rasi=0, retrograde=True)
    assert direct.retrograde is False
    assert retro.retrograde is True


def test_compute_indu_lagna_known_example():
    # Cross-checked by hand in conversation: Lagna=Sagittarius(8), Moon=Taurus(1)
    # -> 9th from Lagna=Leo(Sun,30), 9th from Moon=Capricorn(Saturn,1) -> sum=31
    # -> remainder=7 -> 7 signs forward from Taurus (inclusive) = Scorpio(7)
    assert compute_indu_lagna(lagna_rasi=8, moon_rasi=1) == 7


def test_compute_indu_lagna_remainder_zero_wraps_to_twelve():
    # Lagna=Leo(4): 9th from it is Aries(0), lord Mars (Kala 6).
    # Moon=Pisces(11): 9th from it is Scorpio(7), lord Mars (Kala 6).
    # Sum = 12 -> remainder 0 -> wraps to 12 -> counting 12 signs forward from
    # Moon's own sign (inclusive) wraps all the way around to Aquarius (10).
    assert compute_indu_lagna(lagna_rasi=4, moon_rasi=11) == 10


def test_is_pushkara_navamsa_fire_signs():
    # Aries (fire): divisions 7 & 9 (parts 6 & 8) are pushkara
    assert is_pushkara_navamsa(1.0) is False  # part 0
    assert is_pushkara_navamsa(21.0) is True  # part 6 (7th division)
    assert is_pushkara_navamsa(27.0) is True  # part 8 (9th division)


def test_is_pushkara_navamsa_earth_signs():
    # Taurus (earth, longitude 30-60): divisions 3 & 5 (parts 2 & 4)
    assert is_pushkara_navamsa(31.0) is False  # part 0
    assert is_pushkara_navamsa(37.0) is True  # part 2 (3rd division)
    assert is_pushkara_navamsa(44.0) is True  # part 4 (5th division)


def test_is_pushkara_navamsa_air_signs():
    # Gemini (air, longitude 60-90): divisions 6 & 8 (parts 5 & 7)
    assert is_pushkara_navamsa(61.0) is False  # part 0
    assert is_pushkara_navamsa(77.0) is True  # part 5 (6th division)
    assert is_pushkara_navamsa(84.0) is True  # part 7 (8th division)


def test_is_pushkara_navamsa_water_signs():
    # Cancer (water, longitude 90-120): divisions 1 & 3 (parts 0 & 2)
    assert is_pushkara_navamsa(91.0) is True  # part 0 (1st division)
    assert is_pushkara_navamsa(95.0) is False  # part 1
    assert is_pushkara_navamsa(97.0) is True  # part 2 (3rd division)


def test_make_graha_position_includes_pushkara_navamsa():
    pos = make_graha_position("Sun", 21.0, longitude_to_rasi(21.0), lagna_rasi=0)
    assert pos.pushkara_navamsa is True


# The 24 Pushkara Navamsa padas from Dr. N. G. Kumaran, "Pushkara Navamsa", IJATET 8(1), 2023,
# as (nakshatra index, pada). The paper's table prints Uttara Phalguni 3 and Uttara Bhadrapada 3;
# its own rule (earth signs 3rd/5th, water signs 1st/3rd navamsa) gives 4 and 2, used here.
PAPER_PUSHKARA_PADAS = [
    (1, 3), (2, 1), (2, 4), (3, 2), (5, 4), (6, 2), (6, 4), (7, 2), (10, 3), (11, 1), (11, 4), (12, 2),
    (14, 4), (15, 2), (15, 4), (16, 2), (19, 3), (20, 1), (20, 4), (21, 2), (23, 4), (24, 2), (24, 4), (25, 2),
]


def _pushkara_padas():
    span = 10 / 3
    return [(i // 4, i % 4 + 1) for i in range(108) if is_pushkara_navamsa(i * span + span / 2)]


def test_pushkara_padas_match_the_paper():
    assert _pushkara_padas() == PAPER_PUSHKARA_PADAS


def test_pushkara_padas_by_star_lord():
    from collections import Counter

    counts = Counter(nakshatra_lord(nak) for nak, _ in _pushkara_padas())
    assert counts == {"Sun": 6, "Jupiter": 6, "Venus": 3, "Saturn": 3, "Moon": 3, "Rahu": 3}
    assert not {"Mars", "Mercury", "Ketu"} & set(counts)


def test_reading_page_lists_the_same_padas():
    import re

    js = open("static/labels.js", encoding="utf-8").read()
    block = js[js.index("const PUSHKARA_PADAS = [") : js.index("];", js.index("const PUSHKARA_PADAS = ["))]
    assert [(int(a), int(b)) for a, b in re.findall(r"\[(\d+), (\d)\]", block)] == PAPER_PUSHKARA_PADAS
