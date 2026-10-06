from datetime import date, time
from app.navamsha import build_navamsha_payload


def test_build_navamsha_payload():
    payload = build_navamsha_payload(
        dob=date(1995, 8, 15),
        tob=time(14, 30, 0),
        latitude=13.0827,
        longitude=80.2707,
        timezone_name="Asia/Kolkata",
    )
    assert payload["year"] == 1995
    assert payload["month"] == 8
    assert payload["date"] == 15
    assert payload["hours"] == 14
    assert payload["minutes"] == 30
    assert payload["seconds"] == 0
    assert payload["latitude"] == 13.0827
    assert payload["longitude"] == 80.2707
    assert payload["timezone"] == 5.5
