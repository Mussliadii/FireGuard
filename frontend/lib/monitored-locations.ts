export type MonitoredLocation = {
  name: string;
  lat: number;
  lon: number;
};

// Known peatland/forest fire-prone regions in Indonesia, checked on a
// schedule so risk prediction doesn't depend on someone manually picking a
// point to check — this is what makes module 3 (risk prediction) actually
// preventive instead of only an on-demand, single-point lookup tool.
export const MONITORED_LOCATIONS: MonitoredLocation[] = [
  { name: "Palangkaraya, Central Kalimantan", lat: -2.21, lon: 113.92 },
  { name: "Pontianak, West Kalimantan", lat: -0.03, lon: 109.33 },
  { name: "Banjarmasin, South Kalimantan", lat: -3.32, lon: 114.59 },
  { name: "Pekanbaru, Riau", lat: 0.51, lon: 101.45 },
  { name: "Jambi City, Jambi", lat: -1.61, lon: 103.61 },
  { name: "Palembang, South Sumatra", lat: -2.99, lon: 104.76 },
];
