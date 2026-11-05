export type Hotspot = {
  id: string;
  lat: number;
  lon: number;
  confidence: number;
  risk: "low" | "medium" | "high";
  acquiredAt?: string;
};

// Used when NASA_FIRMS_MAP_KEY hasn't been set yet, so the map can still be
// demoed without an API key.
export const SAMPLE_HOTSPOTS: Hotspot[] = [
  { id: "sample-1", lat: -2.5, lon: 113.0, confidence: 0.82, risk: "high" },
  { id: "sample-2", lat: -0.5, lon: 117.0, confidence: 0.55, risk: "medium" },
];

// Default bounding box: Kalimantan + Sumatra (west,south,east,north).
export const DEFAULT_BBOX = "95,-11,141,6";
