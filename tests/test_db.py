import os
from datetime import date, time

import app.db as db


def test_save_list_get_roundtrip(tmp_path):
    db_file = str(tmp_path / "test_jathakam.db")
    db._engine = None
    db.init_db(db_file)

    chart = db.SavedChart(
        name="Test Person",
        gender="Female",
        dob=date(1990, 5, 15),
        tob=time(10, 30, 0),
        pob_label="Chennai",
        latitude=13.0827,
        longitude=80.2707,
        tz_name="Asia/Kolkata",
        utc_offset=5.5,
        chart_json="{}",
    )
    saved = db.save_chart(chart)
    assert saved.id is not None

    fetched = db.get_chart(saved.id)
    assert fetched is not None
    assert fetched.name == "Test Person"
    assert fetched.dob == date(1990, 5, 15)

    chart2 = db.SavedChart(
        name="Second Person", gender="Male", dob=date(1985, 1, 1), tob=time(0, 0, 0),
        pob_label="Madurai", latitude=9.9252, longitude=78.1198, tz_name="Asia/Kolkata", utc_offset=5.5, chart_json="{}",
    )
    db.save_chart(chart2)

    all_charts = db.list_charts()
    assert len(all_charts) == 2
    assert {c.name for c in all_charts} == {"Test Person", "Second Person"}

    db._engine = None
