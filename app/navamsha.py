import os
from datetime import date, datetime, time
from typing import Any
import httpx
from fastapi import HTTPException

from app.timezone_utils import compute_utc_offset

NAVAMSHA_BASE_URL = os.getenv("NAVAMSHA_BASE_URL", "https://api.navamsha.in")
NAVAMSHA_API_KEY = os.getenv("NAVAMSHA_API_KEY", "vda_live_17dfca51_7YR09PWQi4sL80ylBTZEC6dvRAGWn6SfjhxuhM1G9rw")


def build_navamsha_payload(
    dob: date,
    tob: time,
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> dict[str, Any]:
    """Convert standard app birth details to the payload expected by Navamsha API."""
    utc_offset = compute_utc_offset(timezone_name, dob, tob)
    return {
        "year": dob.year,
        "month": dob.month,
        "date": dob.day,
        "hours": tob.hour,
        "minutes": tob.minute,
        "seconds": tob.second,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": round(utc_offset, 2),
    }


async def call_navamsha_api(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Make an authenticated POST request to Navamsha API."""
    url = f"{NAVAMSHA_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "X-API-Key": NAVAMSHA_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "AstroJeevi/1.0",
    }
    
    async with httpx.AsyncClient(timeout=25.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error connecting to Navamsha API: {exc}")

        if response.status_code != 200:
            try:
                err_data = response.json()
                detail = err_data.get("message") or err_data.get("detail") or response.text
            except Exception:
                detail = response.text
            raise HTTPException(status_code=response.status_code, detail=f"Navamsha API Error: {detail}")

        return response.json()
