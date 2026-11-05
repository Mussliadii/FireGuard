"""Combines NASA FIRMS hotspots + an automated risk-prediction sweep over
known fire-prone regions into one "what's dangerous right now" feed.

This is the automated-prevention counterpart to the on-demand, single-point
risk form: nobody has to pick a location for this to produce a warning.
"""

from dataclasses import dataclass
from typing import Literal

from lib.firms import fetch_firms_hotspots
from lib.monitored_locations import MONITORED_LOCATIONS
from lib.risk_model import RiskInput, predict_risk
from lib.weather import fetch_current_weather


@dataclass
class DangerPoint:
    name: str
    lat: float
    lon: float
    risk: Literal["medium", "high"]
    source: Literal["firms", "prediction"]
    detail: str


def get_firms_danger_points(firms_map_key: str | None) -> list[DangerPoint]:
    hotspots, _ = fetch_firms_hotspots(firms_map_key)
    return [
        DangerPoint(
            name=f"Hotspot ({h.lat:.2f}, {h.lon:.2f})",
            lat=h.lat,
            lon=h.lon,
            risk=h.risk,
            source="firms",
            detail=f"confidence {h.confidence * 100:.0f}%",
        )
        for h in hotspots
        if h.risk != "low"
    ]


def get_prediction_danger_points(risk_model) -> list[DangerPoint]:
    danger_points = []
    for loc in MONITORED_LOCATIONS:
        try:
            weather = fetch_current_weather(loc.lat, loc.lon)
        except Exception:
            continue

        result = predict_risk(
            risk_model,
            RiskInput(
                temperature_c=weather.temperature_c,
                humidity_pct=weather.humidity_pct,
                rainfall_mm=weather.rainfall_mm,
                wind_speed_kmh=weather.wind_speed_kmh,
            ),
        )
        if result["risk_label"] in ("medium", "high"):
            danger_points.append(
                DangerPoint(
                    name=loc.name,
                    lat=loc.lat,
                    lon=loc.lon,
                    risk=result["risk_label"],
                    source="prediction",
                    detail=f"score {result['risk_score'] * 100:.1f}%",
                )
            )
    return danger_points


def get_current_danger_points(firms_map_key: str | None, risk_model) -> list[DangerPoint]:
    return get_firms_danger_points(firms_map_key) + get_prediction_danger_points(risk_model)
