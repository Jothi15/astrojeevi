import os
from datetime import date, datetime, timedelta, timezone

import pytest

from app.astrology import ChartData, GrahaPosition
from app.constants import GRAHA_NAMES
from app.ephemeris import init_ephemeris
from app.navamsa_sashtashtagam import (
    NavamsaPoint,
    compute_navamsa_sashtashtagam,
    houses_ruled,
    navamsa_point,
    transit_windows,
)


def _chart(lagna_rasi: int, rasis: dict[str, int]) -> ChartData:
    grahas = {
        name: GrahaPosition(name, rasi * 30 + 5, rasi, (rasi - lagna_rasi) % 12 + 1, 0, 1, 5.0, "", "", False, False)
        for name, rasi in rasis.items()
    }
    return ChartData(lagna_rasi=lagna_rasi, grahas=grahas)


ALL_ARIES = {name: 0 for name in GRAHA_NAMES}


def test_count_from_d1_rasi_to_d9_rasi():
    d1 = _chart(0, {**ALL_ARIES, "Sun": 8})  # Sun in Dhanus
    for d9_rasi in range(12):
        d9 = _chart(0, {**ALL_ARIES, "Sun": d9_rasi})
        sun = next(e for e in compute_navamsa_sashtashtagam(d1, d9) if e.planet == "Sun")
        assert sun.count == (d9_rasi - 8) % 12 + 1
        assert sun.flagged is (sun.count in (6, 8)), d9_rasi


def test_sun_dhanus_to_rishabam_is_6th():
    # The user's chart: Sun in Dhanus in D1, Rishabam in D9.
    entries = compute_navamsa_sashtashtagam(_chart(8, {**ALL_ARIES, "Sun": 8}), _chart(4, {**ALL_ARIES, "Sun": 1}))
    sun = next(e for e in entries if e.planet == "Sun")
    assert (sun.count, sun.flagged, sun.d1_house) == (6, True, 1)
    assert [e.planet for e in entries if e.flagged] == ["Sun"]


def test_houses_ruled_for_dhanus_lagna():
    assert houses_ruled("Sun", 8) == [9]
    assert houses_ruled("Moon", 8) == [8]
    assert houses_ruled("Mars", 8) == [5, 12]
    assert houses_ruled("Mercury", 8) == [7, 10]
    assert houses_ruled("Jupiter", 8) == [1, 4]
    assert houses_ruled("Venus", 8) == [6, 11]
    assert houses_ruled("Saturn", 8) == [2, 3]
    assert houses_ruled("Rahu", 8) == [] and houses_ruled("Ketu", 8) == []


def test_all_nine_planets_listed():
    entries = compute_navamsa_sashtashtagam(_chart(0, ALL_ARIES), _chart(0, ALL_ARIES))
    assert [e.planet for e in entries] == GRAHA_NAMES
    assert not any(e.flagged for e in entries)


def test_navamsa_point_is_the_pada_of_longitude_times_nine():
    # Sun at Dhanus 5deg35': navamsa longitude 50deg18' = Rishabam 20deg18', Rohini pada 4.
    p = navamsa_point(245.59)
    assert (p.nakshatra, p.pada) == (3, 4)
    assert (round(p.start, 3), round(p.end, 3)) == (50.0, 53.333)


def test_only_flagged_planets_get_a_point():
    d1 = _chart(8, {**ALL_ARIES, "Sun": 8})
    d9 = _chart(4, {**ALL_ARIES, "Sun": 1})
    entries = {e.planet: e for e in compute_navamsa_sashtashtagam(d1, d9)}
    assert entries["Sun"].point is not None and entries["Sun"].transits == []  # no window asked for
    assert all(e.point is None for name, e in entries.items() if name != "Sun")


IST = timezone(timedelta(hours=5, minutes=30))
needs_ephe = pytest.mark.skipif(
    not os.path.exists("ephe/sepl_18.se1"), reason="Swiss Ephemeris data files not present in ephe/"
)


@pytest.fixture()
def ephe():
    init_ephemeris("ephe")


def _dates(windows):
    return [(w.start.astimezone(IST).date(), w.end.astimezone(IST).date()) for w in windows]


@needs_ephe
def test_sun_in_rohini_pada_4_each_june(ephe):
    windows = transit_windows("Sun", navamsa_point(245.59), datetime(2026, 1, 1, tzinfo=IST), datetime(2028, 1, 1, tzinfo=IST))
    assert _dates(windows) == [(date(2026, 6, 5), date(2026, 6, 8)), (date(2027, 6, 5), date(2027, 6, 8))]


@needs_ephe
def test_moon_passes_a_pada_every_month_for_hours(ephe):
    windows = transit_windows("Moon", navamsa_point(35.76), datetime(2026, 1, 1, tzinfo=IST), datetime(2027, 1, 1, tzinfo=IST))
    assert 12 <= len(windows) <= 14
    assert all(timedelta(hours=4) < w.end - w.start < timedelta(hours=9) for w in windows)


@needs_ephe
def test_saturn_retrograde_gives_separate_passes(ephe):
    # Ashwini pada 1 (Mesham 0deg-3deg20'): in Jun 2027, out forward, back in retrograde, out
    # back into Meenam in Oct 2027, then in again in Feb 2028.
    ashwini_1 = NavamsaPoint(0, 1, 0.0, 10 / 3)
    windows = transit_windows("Saturn", ashwini_1, datetime(2027, 1, 1, tzinfo=IST), datetime(2029, 1, 1, tzinfo=IST))
    assert _dates(windows) == [
        (date(2027, 6, 3), date(2027, 7, 22)),
        (date(2027, 8, 28), date(2027, 10, 20)),
        (date(2028, 2, 23), date(2028, 3, 25)),
    ]


@needs_ephe
def test_window_already_running_at_start_is_clipped(ephe):
    start = datetime(2026, 6, 6, tzinfo=IST)
    [w] = transit_windows("Sun", navamsa_point(245.59), start, datetime(2026, 7, 1, tzinfo=IST))
    assert w.start == start.astimezone(timezone.utc) and w.end.astimezone(IST).date() == date(2026, 6, 8)
