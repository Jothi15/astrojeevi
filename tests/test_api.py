import os
from datetime import date, time

import pytest
from fastapi.testclient import TestClient

import app.db as db
from app.ephemeris import init_ephemeris
from app.main import app

pytestmark = pytest.mark.skipif(
    not os.path.exists("ephe/sepl_18.se1"),
    reason="Swiss Ephemeris data files not present in ephe/",
)

BIRTH = {
    "name": "Krithika", "gender": "Female", "dob": "1969-12-21", "tob": "07:25:00",
    "pob_label": "Secunderabad, Telangana, India", "latitude": 17.50427, "longitude": 78.54263,
    "timezone": "Asia/Kolkata",
}


@pytest.fixture()
def client(tmp_path):
    # No `with` block, so the app's startup hook (which opens the real jathakam.db) never runs.
    init_ephemeris("ephe")
    db._engine = None
    db.init_db(str(tmp_path / "api_test.db"))
    yield TestClient(app)
    db._engine = None


def test_old_saved_charts_load_with_all_current_features(client):
    # A row saved by an older version: only birth details, no stored results at all.
    old = db.save_chart(
        db.SavedChart(
            name="Old", gender="Female", dob=date(1969, 12, 21), tob=time(7, 25), pob_label="Secunderabad",
            latitude=17.50427, longitude=78.54263, tz_name="Asia/Kolkata", utc_offset=5.5,
            chart_json='{"d1": {"stale": true}}',
        )
    )
    body = client.get(f"/api/charts/{old.id}").json()
    assert {(e["planet"], e["state"]) for e in body["dignities"]} == {("Moon", "ucham"), ("Saturn", "neecham")}
    assert len(body["yogas"]) == 12
    assert not next(y for y in body["yogas"] if y["name"] == "Jeevanam Yoga")["triggered"]  # Moon in Rishabam -> 2nd house Makaram is empty
    assert not next(y for y in body["yogas"] if y["name"] == "Soorya Chandraadhi Yoga")["triggered"]  # Sun house 1 -> Mesha; Moon in Rishabam
    assert "gulika" in body and "mandi" in body
    assert body["pranapada"]["rasi"] == 7  # Scorpio
    tithi = body["tithi"]
    assert (tithi["number"], tithi["paksha"]) == (13, "shukla")  # Shukla Trayodasi
    assert [(r["rasi"], r["house"], r["planets"]) for r in tithi["soonya_rasis"]] == [
        (1, 6, ["Moon"]),
        (4, 9, ["Ketu"]),
    ]
    mudakku = body["mudakku"]
    assert (mudakku["sun_pada"], mudakku["count"]) == (2, 1)  # Sun in Moolam pada 2
    assert (mudakku["nakshatra"], mudakku["pada"], mudakku["rasi"], mudakku["house"]) == (18, 2, 8, 1)
    assert (mudakku["rasi_lord"], mudakku["star_lord"]) == ("Jupiter", "Ketu")
    assert mudakku["planets"] == ["Sun", "Mercury"] and mudakku["is_lagna"]
    assert body["upasana"] == {"planet": "Venus", "planet_rasi": 7, "rasi": 5}  # Venus in Scorpio -> 11th is Virgo
    drekkana = {e["planet"]: e for e in body["drekkana_lords"]}
    assert len(drekkana) == 9 and not any(e["weakened"] for e in drekkana.values())
    assert (drekkana["Rahu"]["controller"], drekkana["Rahu"]["count"]) == ("Venus", 10)  # 3rd: Thulam
    assert (drekkana["Ketu"]["controller"], drekkana["Ketu"]["count"]) == ("Mars", 7)  # 3rd: Mesham
    assert (drekkana["Mars"]["drekkana"], drekkana["Mars"]["controller"], drekkana["Mars"]["count"]) == (2, "Mercury", 11)
    assert (drekkana["Venus"]["drekkana"], drekkana["Venus"]["controller"], drekkana["Venus"]["count"]) == (3, "Moon", 7)
    sashtashtagam = {e["planet"]: e for e in body["navamsa_sashtashtagam"]}
    assert [p for p, e in sashtashtagam.items() if e["flagged"]] == ["Sun"]  # Dhanus -> Rishabam in D9
    assert (sashtashtagam["Sun"]["count"], sashtashtagam["Sun"]["houses_ruled"]) == (6, [9])
    assert sashtashtagam["Rahu"]["houses_ruled"] == [] and sashtashtagam["Rahu"]["d1_house"] == 3
    assert (sashtashtagam["Sun"]["point"]["nakshatra"], sashtashtagam["Sun"]["point"]["pada"]) == (3, 4)  # Rohini 4
    assert len(sashtashtagam["Sun"]["transits"]) == 6  # every June, 2026 to 2031
    assert sashtashtagam["Sun"]["transits"][0]["start"].startswith("2026-06-05T")
    assert sashtashtagam["Moon"]["point"] is None and sashtashtagam["Moon"]["transits"] == []
    peyarchis = body["peyarchis"]
    assert [p["planet"] for p in peyarchis if p["in_effect_at_start"]] == ["Saturn", "Rahu", "Jupiter"]
    assert peyarchis[0]["when"] == "2025-03-29T21:45:09+05:30"  # Saturn into Pisces, in the chart's time zone
    assert (peyarchis[0]["moon_rasi"], peyarchis[0]["count"], peyarchis[0]["moorthi"]) == (11, 11, "Swarna")
    assert body["kaala_pakai"] == [
        {"planet": "Moon", "rasi": 1, "house": 6},  # Taurus
        {"planet": "Mercury", "rasi": 8, "house": 1},  # Sagittarius
        {"planet": "Jupiter", "rasi": 6, "house": 11},  # Libra
    ]


def test_create_then_load_matches(client):
    created = client.post("/api/chart", json=BIRTH).json()
    loaded = client.get(f"/api/charts/{created['id']}").json()
    assert created["d1"] == loaded["d1"]
    assert created["dignities"] == loaded["dignities"]


def test_delete_chart(client):
    chart_id = client.post("/api/chart", json=BIRTH).json()["id"]
    assert len(client.get("/api/charts").json()) == 1
    assert client.delete(f"/api/charts/{chart_id}").status_code == 204
    assert client.get("/api/charts").json() == []
    assert client.get(f"/api/charts/{chart_id}").status_code == 404


def test_delete_missing_chart_is_404(client):
    assert client.delete("/api/charts/999").status_code == 404


def test_prasannam_at_a_given_moment(client):
    # Jupiter's entry into Capricorn, 20 Nov 2020 12:41:55 IST (Astroshala): the Moon was in Capricorn.
    body = client.get(
        "/api/prasannam",
        params={"latitude": 13.08784, "longitude": 80.27847, "timezone": "Asia/Kolkata", "at": "2020-11-20T12:41:55+05:30"},
    ).json()
    assert body["when"] == "2020-11-20T12:41:55+05:30"
    moon = body["d1"]["grahas"]["Moon"]
    assert moon["rasi"] == 9 and 0 <= moon["degree_in_sign"] < 30 and 1 <= moon["pada"] <= 4
    assert moon["nakshatra"] in (20, 21, 22)  # Capricorn holds Uttarashada 2-4, Shravana, Dhanishta 1-2
    # The app's ephemeris puts Jupiter's ingress 42 minutes later (13:23 IST), so it is still
    # at the very end of Sagittarius here.
    jupiter = body["d1"]["grahas"]["Jupiter"]
    assert jupiter["rasi"] == 8 and jupiter["degree_in_sign"] > 29.99
    assert body["d1"]["lagna_rasi"] == int(body["lagna_longitude"] // 30)


def test_prasannam_now_uses_the_time_zone(client):
    body = client.get("/api/prasannam", params={"latitude": 13.08, "longitude": 80.27, "timezone": "Asia/Kolkata"}).json()
    assert body["when"].endswith("+05:30") and len(body["d1"]["grahas"]) == 9


def test_prasannam_rejects_an_unknown_time_zone(client):
    res = client.get("/api/prasannam", params={"latitude": 13.08, "longitude": 80.27, "timezone": "Not/AZone"})
    assert res.status_code == 400
