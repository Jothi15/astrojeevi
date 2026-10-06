"""
Integration tests against the real Swiss Ephemeris data files in ephe/.

These check internal consistency and wiring (Julian day conversion, sidereal
mode, node selection, output ranges) rather than exact published values,
since no independently-verified reference chart was available at write time.
For stronger verification, replace test_matches_known_reference_chart below
with a real birth chart whose lagna/rasi/nakshatra you already trust (e.g.
your own, cross-checked on astro.com set to Sidereal/Lahiri).
"""

from datetime import date, time

import pytest

from app.ephemeris import compute_ascendant, compute_graha_longitudes, init_ephemeris, to_julian_day_ut

pytestmark = pytest.mark.skipif(
    not __import__("os").path.exists("ephe/sepl_18.se1"),
    reason="Swiss Ephemeris data files not present in ephe/",
)


@pytest.fixture(autouse=True, scope="module")
def _init():
    init_ephemeris("ephe")


def test_graha_longitudes_in_valid_range():
    jd = to_julian_day_ut(date(1990, 5, 15), time(10, 30, 0), 5.5)
    longitudes = compute_graha_longitudes(jd)
    assert set(longitudes.keys()) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
    for name, lon in longitudes.items():
        assert 0 <= lon < 360, f"{name} longitude {lon} out of range"


def test_ketu_is_opposite_rahu():
    jd = to_julian_day_ut(date(1990, 5, 15), time(10, 30, 0), 5.5)
    longitudes = compute_graha_longitudes(jd)
    diff = abs(longitudes["Ketu"] - longitudes["Rahu"])
    assert abs(diff - 180) < 1e-6 or abs(diff - 180 - 360) < 1e-6


def test_ascendant_in_valid_range():
    jd = to_julian_day_ut(date(1990, 5, 15), time(10, 30, 0), 5.5)
    asc = compute_ascendant(jd, 13.0827, 80.2707)
    assert 0 <= asc < 360


def test_computation_is_deterministic():
    jd = to_julian_day_ut(date(1990, 5, 15), time(10, 30, 0), 5.5)
    result1 = compute_graha_longitudes(jd)
    result2 = compute_graha_longitudes(jd)
    assert result1 == result2


def test_moon_moves_faster_than_sun_over_a_day():
    jd1 = to_julian_day_ut(date(1990, 5, 15), time(0, 0, 0), 0)
    jd2 = to_julian_day_ut(date(1990, 5, 16), time(0, 0, 0), 0)
    l1 = compute_graha_longitudes(jd1)
    l2 = compute_graha_longitudes(jd2)
    moon_delta = (l2["Moon"] - l1["Moon"]) % 360
    sun_delta = (l2["Sun"] - l1["Sun"]) % 360
    assert moon_delta > sun_delta
