"""Known peatland/forest fire-prone regions in Indonesia.

Checked automatically on a schedule (or on each app load, for this Streamlit
version) so risk prediction doesn't depend on someone manually picking a
point to check — this is what makes the risk module actually preventive
instead of only an on-demand, single-point lookup tool.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MonitoredLocation:
    name: str
    lat: float
    lon: float


MONITORED_LOCATIONS = [
    MonitoredLocation("Palangkaraya, Central Kalimantan", -2.21, 113.92),
    MonitoredLocation("Pontianak, West Kalimantan", -0.03, 109.33),
    MonitoredLocation("Banjarmasin, South Kalimantan", -3.32, 114.59),
    MonitoredLocation("Pekanbaru, Riau", 0.51, 101.45),
    MonitoredLocation("Jambi City, Jambi", -1.61, 103.61),
    MonitoredLocation("Palembang, South Sumatra", -2.99, 104.76),
]
