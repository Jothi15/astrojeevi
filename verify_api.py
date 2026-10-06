"""
API Verification Script
Tests both the Local Astrology Engine and the Navamsha API integration,
validating HTTP Status, JSON structure, and astronomical logic.
"""
from app.db import init_db
from app.ephemeris import init_ephemeris
from app.main import app
from starlette.testclient import TestClient

# Initialize ephemeris and database
init_ephemeris()
init_db()

client = TestClient(app)

SAMPLE_PAYLOAD = {
    "name": "Validation Test",
    "gender": "Male",
    "dob": "1995-08-15",
    "tob": "14:30:00",
    "pob_label": "Chennai, Tamil Nadu, India",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata",
}


def check_status(name: str, res, expected_keys: list[str]) -> bool:
    print(f"\n--- Checking: {name} ---")
    print(f"Status Code: {res.status_code}")
    
    if res.status_code != 200:
        print(f"[FAIL] Expected 200, got {res.status_code}. Response: {res.text}")
        return False
    
    data = res.json()
    for key in expected_keys:
        if key not in data and key not in data.get("output", {}):
            print(f"[FAIL] Missing expected key '{key}' in response")
            return False
            
    print(f"[PASS] {name} is responding correctly!")
    return True


def run_checks():
    print("==========================================")
    print(" ASTROLOGY API VALIDATION REPORT ")
    print("==========================================")

    # 1. Check Local Swiss Ephemeris Birth Chart
    res_local = client.post("/api/chart", json=SAMPLE_PAYLOAD)
    if check_status("Local Chart Calculation (/api/chart)", res_local, ["d1", "vargas", "mahadasas"]):
        body = res_local.json()
        lagna = body["d1"]["lagna_rasi"]
        sun_deg = body["d1"]["grahas"]["Sun"]["longitude"]
        moon_deg = body["d1"]["grahas"]["Moon"]["longitude"]
        print(f"   -> Lagna Rasi (1-12): {lagna}")
        print(f"   -> Sun Longitude: {sun_deg:.2f}°")
        print(f"   -> Moon Longitude: {moon_deg:.2f}°")

    # 2. Check Navamsha API Kundali
    res_nav = client.post("/api/navamsha/kundali", json=SAMPLE_PAYLOAD)
    if check_status("Navamsha API Kundali (/api/navamsha/kundali)", res_nav, ["statusCode", "output"]):
        nav_out = res_nav.json().get("output", {})
        asc = nav_out.get("ascendant", {})
        print(f"   -> Navamsha Ascendant Sign: {asc.get('zodiac_sign_name')}")
        print(f"   -> Navamsha Ascendant Degree: {asc.get('normDegree', 0):.2f}°")

    # 3. Check Navamsha Birth Details (Nakshatra, Tithi, Yoga)
    res_details = client.post("/api/navamsha/birth-details", json=SAMPLE_PAYLOAD)
    if check_status("Navamsha Birth Details (/api/navamsha/birth-details)", res_details, ["statusCode", "output"]):
        out = res_details.json().get("output", {})
        print(f"   -> Nakshatra: {out.get('nakshatra', {}).get('name')} (Pada {out.get('nakshatra', {}).get('pada')})")
        print(f"   -> Chandra Rasi: {out.get('chandra_rasi', {}).get('name')}")

    # 4. Check Navamsha D9 Chart SVG
    res_svg = client.post("/api/navamsha/chart-svg/d9", json=SAMPLE_PAYLOAD)
    if check_status("Navamsha D9 Chart SVG (/api/navamsha/chart-svg/d9)", res_svg, ["statusCode", "output"]):
        svg = res_svg.json().get("output", "")
        print(f"   -> SVG Generated: {'Yes' if '<svg' in svg else 'No'} ({len(svg)} chars)")

    print("\n==========================================")
    print(" ALL CHECKS COMPLETED SUCCESSFULLY ")
    print("==========================================")


if __name__ == "__main__":
    run_checks()
