"""NASA FIRMS active-fire hotspots, with a sample-data fallback.

Used both for the monitoring map and as one of the two automatic signals
feeding the live danger feed (the other being lib.risk_model's sweep over
MONITORED_LOCATIONS).
"""

from dataclasses import dataclass
from typing import Literal

import requests

FIRMS_SOURCE = "VIIRS_SNPP_NRT"
DAY_RANGE = 1
DEFAULT_BBOX = "95,-11,141,6"  # Kalimantan + Sumatra: west,south,east,north

Risk = Literal["low", "medium", "high"]


@dataclass
class Hotspot:
    id: str
    lat: float
    lon: float
    confidence: float
    risk: Risk
    acquired_at: str | None = None


SAMPLE_HOTSPOTS = [
    Hotspot(id="sample-1", lat=-2.5, lon=113.0, confidence=0.82, risk="high"),
    Hotspot(id="sample-2", lat=-0.5, lon=117.0, confidence=0.55, risk="medium"),
]


def _to_risk(confidence_raw: str) -> Risk:
    """VIIRS confidence is categorical (l/n/h); MODIS confidence is 0-100."""
    normalized = confidence_raw.strip().lower()
    if normalized in ("h", "high"):
        return "high"
    if normalized in ("n", "nominal"):
        return "medium"
    if normalized in ("l", "low"):
        return "low"

    try:
        numeric = float(normalized)
    except ValueError:
        return "low"
    if numeric >= 80:
        return "high"
    if numeric >= 50:
        return "medium"
    return "low"


def _parse_firms_csv(csv_text: str) -> list[Hotspot]:
    lines = csv_text.strip().split("\n")
    if len(lines) < 2:
        return []

    header = [h.strip() for h in lines[0].split(",")]
    try:
        lat_idx = header.index("latitude")
        lon_idx = header.index("longitude")
    except ValueError:
        return []
    conf_idx = header.index("confidence") if "confidence" in header else -1
    date_idx = header.index("acq_date") if "acq_date" in header else -1

    hotspots = []
    for i, line in enumerate(lines[1:]):
        cols = line.split(",")
        confidence_raw = cols[conf_idx] if conf_idx != -1 else "n"
        try:
            confidence = float(confidence_raw) / 100
        except ValueError:
            confidence = 0.5
        hotspots.append(
            Hotspot(
                id=f"firms-{i}",
                lat=float(cols[lat_idx]),
                lon=float(cols[lon_idx]),
                confidence=confidence,
                risk=_to_risk(confidence_raw),
                acquired_at=cols[date_idx] if date_idx != -1 else None,
            )
        )
    return hotspots


def fetch_firms_hotspots(
    map_key: str | None, bbox: str = DEFAULT_BBOX, timeout: int = 20
) -> tuple[list[Hotspot], Literal["firms", "sample"]]:
    if not map_key:
        return SAMPLE_HOTSPOTS, "sample"

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{FIRMS_SOURCE}/{bbox}/{DAY_RANGE}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        hotspots = _parse_firms_csv(response.text)
        return hotspots, "firms"
    except Exception:
        return SAMPLE_HOTSPOTS, "sample"
