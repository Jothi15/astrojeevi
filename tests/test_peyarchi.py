import os
from datetime import datetime, timedelta, timezone

import pytest

from app.constants import MOORTHI_BY_COUNT
from app.ephemeris import init_ephemeris, jd_from_datetime
from app.peyarchi import compute_peyarchis, find_ingresses, moorthi_for

IST = timezone(timedelta(hours=5, minutes=30))
needs_ephe = pytest.mark.skipif(
    not os.path.exists("ephe/sepl_18.se1"), reason="Swiss Ephemeris data files not present in ephe/"
)


@pytest.fixture(autouse=True)
def ephe():
    if os.path.exists("ephe/sepl_18.se1"):
        init_ephemeris("ephe")


def test_moorthi_table():
    assert {c for c, m in MOORTHI_BY_COUNT.items() if m == "Swarna"} == {1, 6, 11}
    assert {c for c, m in MOORTHI_BY_COUNT.items() if m == "Rajatha"} == {2, 5, 9}
    assert {c for c, m in MOORTHI_BY_COUNT.items() if m == "Thamira"} == {3, 7, 10}
    assert {c for c, m in MOORTHI_BY_COUNT.items() if m == "Loha"} == {4, 8, 12}


def test_article_example_moon_in_capricorn():
    # astroshala.com: Jupiter into Capricorn, 20 Nov 2020, Moon in Capricorn; result per janma rasi.
    expected = ["Thamira", "Rajatha", "Loha", "Thamira", "Swarna", "Rajatha",
                "Loha", "Thamira", "Rajatha", "Swarna", "Loha", "Swarna"]
    assert [moorthi_for(janma, 9)[1] for janma in range(12)] == expected
    assert moorthi_for(0, 9)[0] == 10  # Aries to Capricorn is the 10th


def _window(start: datetime, days: int):
    return compute_peyarchis(1, start, start + timedelta(days=days))


@needs_ephe
def test_jupiter_into_capricorn_2020_matches_article():
    entries = [e for e in _window(datetime(2020, 11, 1, tzinfo=IST), 30) if e.planet == "Jupiter" and e.rasi == 9]
    [e] = [e for e in entries if not e.in_effect_at_start]
    # Article: 12:41:55 IST; ephemeris differences of under an hour are expected.
    assert abs(e.when - datetime(2020, 11, 20, 12, 41, 55, tzinfo=IST)) < timedelta(hours=1)
    assert e.moon_rasi == 9


@needs_ephe
def test_saturn_into_pisces_2025():
    [e] = [e for e in _window(datetime(2025, 3, 1, tzinfo=IST), 60) if e.planet == "Saturn" and not e.in_effect_at_start]
    assert e.rasi == 11 and e.when.astimezone(IST).date() == datetime(2025, 3, 29).date()


@needs_ephe
def test_jupiter_retrograde_slip_and_reentry_2021():
    # Jupiter entered Aquarius in Apr 2021, slipped back into Capricorn in Sep, re-entered in Nov.
    start = datetime(2021, 1, 1, tzinfo=timezone.utc)
    events = find_ingresses("Jupiter", jd_from_datetime(start), jd_from_datetime(start + timedelta(days=365)))
    assert [(e.rasi, e.kind) for e in events] == [(10, "normal"), (9, "retrograde"), (10, "re-entry")]


@needs_ephe
def test_rahu_moves_backwards_and_is_never_marked_retrograde():
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    events = find_ingresses("Rahu", jd_from_datetime(start), jd_from_datetime(start + timedelta(days=3650)))
    assert len(events) >= 5
    assert all(e.kind == "normal" for e in events)
    assert all((b.rasi - a.rasi) % 12 == 11 for a, b in zip(events, events[1:]))


@needs_ephe
def test_window_keeps_one_entry_in_effect_per_planet():
    entries = compute_peyarchis(1, datetime(2026, 1, 1, tzinfo=IST), datetime(2032, 1, 1, tzinfo=IST))
    carried = [e for e in entries if e.in_effect_at_start]
    assert sorted(e.planet for e in carried) == ["Jupiter", "Rahu", "Saturn"]
    assert all(e.when < datetime(2026, 1, 1, tzinfo=IST) for e in carried)
    assert all(e.when < datetime(2032, 1, 1, tzinfo=IST) for e in entries)
    assert entries == sorted(entries, key=lambda e: e.when)
    for e in entries:
        assert (e.count, e.moorthi) == moorthi_for(1, e.moon_rasi)
