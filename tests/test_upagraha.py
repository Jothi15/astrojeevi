"""
Integration tests against the real Swiss Ephemeris data files in ephe/.
Gulika/Mandi need sunrise/sunset (swe.rise_trans), so they can't be tested as
pure math.
"""

import os
from datetime import date, time

import pytest

from app.ephemeris import init_ephemeris
from app.upagraha import compute_gulika_longitude, compute_mandi_longitude

pytestmark = pytest.mark.skipif(
    not os.path.exists("ephe/sepl_18.se1"),
    reason="Swiss Ephemeris data files not present in ephe/",
)


@pytest.fixture(autouse=True, scope="module")
def _init():
    init_ephemeris("ephe")


def test_known_reference_values():
    # Cross-checked by hand in conversation: Sunday day-birth, Secunderabad.
    # Sunrise 06:41 IST, sunset 17:46 IST, Sunday's day table -> Saturn's 7th of 8
    # segments -> starts 15:00 IST, segment length ~1h23m.
    # Gulika = ascendant at segment start; Mandi = ascendant at segment middle.
    gulika = compute_gulika_longitude(date(1969, 12, 21), time(7, 25, 0), 5.5, 17.50427, 78.54263)
    mandi = compute_mandi_longitude(date(1969, 12, 21), time(7, 25, 0), 5.5, 17.50427, 78.54263)
    assert abs(gulika - 25.590976543263974) < 1e-6
    assert abs(mandi - 36.69517874699844) < 1e-6


def test_gulika_and_mandi_are_generally_different_points():
    # They're derived from the same Saturn segment but at different moments
    # within it, so they need not (and for this chart, don't) coincide.
    gulika = compute_gulika_longitude(date(1969, 12, 21), time(7, 25, 0), 5.5, 17.50427, 78.54263)
    mandi = compute_mandi_longitude(date(1969, 12, 21), time(7, 25, 0), 5.5, 17.50427, 78.54263)
    assert gulika != mandi


def test_result_in_valid_range():
    for fn in (compute_gulika_longitude, compute_mandi_longitude):
        lon = fn(date(1990, 5, 15), time(10, 30, 0), 5.5, 13.0827, 80.2707)
        assert 0 <= lon < 360


def test_deterministic():
    args = (date(1990, 5, 15), time(10, 30, 0), 5.5, 13.0827, 80.2707)
    for fn in (compute_gulika_longitude, compute_mandi_longitude):
        assert fn(*args) == fn(*args)


def test_night_birth_before_sunrise_does_not_crash():
    # Birth well before sunrise -> exercises the "previous night" branch
    for fn in (compute_gulika_longitude, compute_mandi_longitude):
        lon = fn(date(1990, 5, 15), time(2, 0, 0), 5.5, 13.0827, 80.2707)
        assert 0 <= lon < 360


def test_night_birth_after_sunset_does_not_crash():
    for fn in (compute_gulika_longitude, compute_mandi_longitude):
        lon = fn(date(1990, 5, 15), time(22, 0, 0), 5.5, 13.0827, 80.2707)
        assert 0 <= lon < 360
