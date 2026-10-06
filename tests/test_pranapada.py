import os
from datetime import date, time

import pytest

from app.ephemeris import init_ephemeris
from app.pranapada import (
    compute_pranapada_longitude,
    ishta_kala_hours,
    pranapada_longitude,
    sun_sign_offset,
)


def test_sun_sign_offsets():
    assert sun_sign_offset(0) == 0.0  # Aries, movable
    assert sun_sign_offset(2) == 120.0  # Gemini, dual
    assert sun_sign_offset(4) == 240.0  # Leo, fixed
    assert sun_sign_offset(8) == 120.0  # Sagittarius, dual
    assert sun_sign_offset(9) == 0.0  # Capricorn, movable


def test_five_degrees_per_minute():
    base = pranapada_longitude(10.0, 1.0)
    assert abs(((pranapada_longitude(10.0, 1.0 + 1 / 60) - base) % 360) - 5.0) < 1e-9


def test_blog_worked_example():
    # Worked example published with the BPHS method: Sun Leo 7deg55'32" (fixed, +240),
    # ishta kala 9.0314 h -> Libra 17deg20'. Uses the article's stated ishta kala.
    sun = 120 + 7 + 55 / 60 + 32 / 3600
    result = pranapada_longitude(sun, 9.0314)
    assert 180 <= result < 210  # Libra
    assert abs(result - (180 + 17 + 20 / 60)) < 0.1


def test_bphs_movable_and_dual_examples():
    # Aries 15deg (movable) + 170deg -> Libra 5deg; ishta kala chosen so the added arc is 170
    assert abs(pranapada_longitude(15.0, 170 / 300) - 185.0) < 1e-9
    # Gemini 15deg (dual, +120) + 170 -> 305 (Aquarius 5deg)
    assert abs(pranapada_longitude(75.0, 170 / 300) - 5.0) < 1e-9  # 75+120+170 = 365 -> 5


needs_ephe = pytest.mark.skipif(
    not os.path.exists("ephe/sepl_18.se1"), reason="Swiss Ephemeris data files not present in ephe/"
)


@needs_ephe
def test_krithika_chart_matches_hand_computation():
    init_ephemeris("ephe")
    hours = ishta_kala_hours(date(1969, 12, 21), time(7, 25), 5.5, 17.50427, 78.54263)
    assert abs(hours - 0.7316) < 0.001  # sunrise ~06:41 IST
    lon = compute_pranapada_longitude(date(1969, 12, 21), time(7, 25), 5.5, 17.50427, 78.54263, 245.5936)
    assert abs(lon - 225.067) < 0.01  # Scorpio 15deg04'


@needs_ephe
def test_birth_before_sunrise_counts_from_previous_sunrise():
    init_ephemeris("ephe")
    hours = ishta_kala_hours(date(1969, 12, 21), time(4, 0), 5.5, 17.50427, 78.54263)
    assert 20 < hours < 24  # ~21.3 h after the previous day's sunrise, not negative
