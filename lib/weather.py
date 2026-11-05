"""Open-Meteo client: free, no API key, safe to call directly."""

from dataclasses import dataclass

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass
class CurrentWeather:
    temperature_c: float
    humidity_pct: float
    rainfall_mm: float
    wind_speed_kmh: float


def fetch_current_weather(lat: float, lon: float, timeout: int = 15) -> CurrentWeather:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=timeout)
    response.raise_for_status()
    current = response.json()["current"]

    return CurrentWeather(
        temperature_c=current["temperature_2m"],
        humidity_pct=current["relative_humidity_2m"],
        rainfall_mm=current["precipitation"],
        wind_speed_kmh=current["wind_speed_10m"],
    )
