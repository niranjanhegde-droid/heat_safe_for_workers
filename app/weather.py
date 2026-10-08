import time
import httpx

_CACHE: dict = {}
TTL = 1800  # seconds


async def fetch_hours(lat: float, lon: float) -> list[dict]:
    """Hourly forecast for today from Open-Meteo (free, no API key). Cached per ~10 km cell."""
    key = (round(lat, 1), round(lon, 1))
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < TTL:
        return hit[1]
    params = {"latitude": lat, "longitude": lon, "forecast_days": 1, "timezone": "auto",
              "wind_speed_unit": "ms",
              "hourly": "temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_10m"}
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get("https://api.open-meteo.com/v1/forecast", params=params)
        r.raise_for_status()
    h = r.json()["hourly"]
    hours = [{"time": t, "temp": a, "rh": b, "solar": s or 0, "wind": max(0.5, (w or 0) * 0.6)}  # 10 m -> worker height
             for t, a, b, s, w in zip(h["time"], h["temperature_2m"], h["relative_humidity_2m"],
                                      h["shortwave_radiation"], h["wind_speed_10m"])]
    _CACHE[key] = (time.time(), hours)
    return hours
