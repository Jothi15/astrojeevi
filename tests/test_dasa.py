from datetime import datetime, timedelta

from app.constants import DASA_ORDER, DASA_YEARS
from app.dasa import compute_mahadasas, compute_sub_periods, moon_nakshatra_balance


def test_dasa_years_sum_to_120():
    assert sum(DASA_YEARS.values()) == 120


def test_moon_nakshatra_balance_at_boundary():
    # exactly at the start of a nakshatra -> full duration remains
    lord, balance = moon_nakshatra_balance(0.0)  # start of Ashwini -> Ketu
    assert lord == "Ketu"
    assert balance == DASA_YEARS["Ketu"]


def test_moon_nakshatra_balance_at_midpoint():
    span = 360 / 27
    lord, balance = moon_nakshatra_balance(span / 2)
    assert lord == "Ketu"
    assert abs(balance - DASA_YEARS["Ketu"] / 2) < 1e-9


def test_mahadasa_sequence_no_gaps_and_correct_total():
    birth = datetime(2000, 1, 1)
    periods = compute_mahadasas(birth, moon_longitude=0.0, years_to_cover=120)
    assert periods[0].start == birth
    for i in range(len(periods) - 1):
        assert periods[i].end == periods[i + 1].start
    total_days = (periods[-1].end - periods[0].start).total_seconds() / 86400
    assert abs(total_days - 120 * 365.25) < 1


def test_compute_sub_periods_sums_to_parent_duration():
    parent_start = datetime(2000, 1, 1)
    parent_end = datetime(2010, 1, 1)
    children = compute_sub_periods("Sun", parent_start, parent_end, "antardasa")
    assert len(children) == 9
    assert children[0].start == parent_start
    assert children[-1].end == parent_end
    for i in range(len(children) - 1):
        assert children[i].end == children[i + 1].start
    # sub-lords cycle DASA_ORDER starting from the parent lord
    start_idx = DASA_ORDER.index("Sun")
    expected_lords = [DASA_ORDER[(start_idx + i) % 9] for i in range(9)]
    assert [c.lord for c in children] == expected_lords


def test_compute_sub_periods_recursive_levels():
    # The same function drives every level below Mahadasa: Antardasa -> Antaram -> Sookshma -> Prana
    parent_start = datetime(2000, 1, 1)
    parent_end = datetime(2010, 1, 1)
    antardasas = compute_sub_periods("Moon", parent_start, parent_end, "antardasa")
    first_antardasa = antardasas[0]
    antarams = compute_sub_periods(first_antardasa.lord, first_antardasa.start, first_antardasa.end, "antaram")
    assert antarams[0].start == first_antardasa.start
    assert antarams[-1].end == first_antardasa.end
    sookshmas = compute_sub_periods(antarams[0].lord, antarams[0].start, antarams[0].end, "sookshma")
    pranas = compute_sub_periods(sookshmas[0].lord, sookshmas[0].start, sookshmas[0].end, "prana")
    assert pranas[0].start == sookshmas[0].start
    # Four levels of chained float division accumulate sub-microsecond drift; a
    # millisecond tolerance is far tighter than anything meaningful for a birth chart.
    assert abs(pranas[-1].end - sookshmas[0].end) < timedelta(milliseconds=1)
