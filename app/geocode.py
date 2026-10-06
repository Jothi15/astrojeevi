import httpx

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def search_places(query: str, count: int = 5) -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(GEOCODE_URL, params={"name": query, "count": count})
        resp.raise_for_status()
        data = resp.json()

    results = []
    for r in data.get("results", []):
        label_parts = [r["name"]]
        if r.get("admin1") and r["admin1"] != r["name"]:
            label_parts.append(r["admin1"])
        if r.get("country"):
            label_parts.append(r["country"])
        results.append(
            {
                "label": ", ".join(label_parts),
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "timezone": r["timezone"],
            }
        )
    return results
