from datetime import date, time

from app.timezone_utils import compute_utc_offset


def test_india_offset_is_constant_no_dst():
    assert compute_utc_offset("Asia/Kolkata", date(1990, 5, 15), time(10, 30)) == 5.5
    assert compute_utc_offset("Asia/Kolkata", date(1990, 1, 1), time(0, 0)) == 5.5


def test_us_eastern_dst_summer_vs_winter():
    summer = compute_utc_offset("America/New_York", date(1990, 7, 1), time(12, 0))
    winter = compute_utc_offset("America/New_York", date(1990, 1, 1), time(12, 0))
    assert summer == -4.0
    assert winter == -5.0
