from app.mudakku import MOOLAM, mudakku_point, pada_rasi


def test_count_runs_to_the_same_pada_of_moolam():
    # Uthirattathi -> Moolam is 20 stars = 80 padas, plus the starting pada
    for pada in range(1, 5):
        assert mudakku_point(25, pada) == (81, 11, pada)  # lands on Uthiram, same pada


def test_uthiram_pada_decides_leo_or_virgo():
    assert pada_rasi(11, 1) == 4  # Uthiram pada 1: Leo
    assert pada_rasi(11, 2) == 5  # Uthiram padas 2-4: Virgo
    assert pada_rasi(11, 4) == 5


def test_sun_in_moolam_lands_on_its_own_pada():
    assert mudakku_point(MOOLAM, 2) == (1, MOOLAM, 2)
    assert pada_rasi(MOOLAM, 2) == 8  # Sagittarius


def test_sun_in_pooradam_counts_all_the_way_round():
    count, nak, pada = mudakku_point(19, 3)  # Pooradam: 26 stars to Moolam
    assert count == 4 * 26 + 1
    assert (nak, pada) == (17, 3)  # Kettai pada 3


def test_pada_rasi_boundaries():
    assert pada_rasi(0, 1) == 0  # Ashwini 1, Aries
    assert pada_rasi(2, 1) == 0  # Karthigai 1 is in Aries
    assert pada_rasi(2, 2) == 1  # Karthigai 2-4 are in Taurus
    assert pada_rasi(26, 4) == 11  # Revathi 4, Pisces
