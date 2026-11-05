import { DEFAULT_BBOX, Hotspot, SAMPLE_HOTSPOTS } from "./hotspots";

const FIRMS_SOURCE = "VIIRS_SNPP_NRT";
const DAY_RANGE = 1;

// VIIRS confidence is categorical (l/n/h); MODIS confidence is 0-100. Handle
// both so swapping FIRMS_SOURCE later doesn't silently break the mapping.
function toRisk(confidence: string): Hotspot["risk"] {
  const normalized = confidence.trim().toLowerCase();
  if (normalized === "h" || normalized === "high") return "high";
  if (normalized === "n" || normalized === "nominal") return "medium";
  if (normalized === "l" || normalized === "low") return "low";

  const numeric = Number(normalized);
  if (!Number.isNaN(numeric)) {
    if (numeric >= 80) return "high";
    if (numeric >= 50) return "medium";
    return "low";
  }
  return "low";
}

function parseFirmsCsv(csv: string): Hotspot[] {
  const lines = csv.trim().split("\n");
  if (lines.length < 2) return [];

  const header = lines[0].split(",").map((h) => h.trim());
  const latIdx = header.indexOf("latitude");
  const lonIdx = header.indexOf("longitude");
  const confIdx = header.indexOf("confidence");
  const dateIdx = header.indexOf("acq_date");

  if (latIdx === -1 || lonIdx === -1) return [];

  return lines.slice(1).map((line, i) => {
    const cols = line.split(",");
    const confidenceRaw = confIdx !== -1 ? cols[confIdx] : "n";
    return {
      id: `firms-${i}`,
      lat: parseFloat(cols[latIdx]),
      lon: parseFloat(cols[lonIdx]),
      confidence: Number.isNaN(Number(confidenceRaw)) ? 0.5 : Number(confidenceRaw) / 100,
      risk: toRisk(confidenceRaw),
      acquiredAt: dateIdx !== -1 ? cols[dateIdx] : undefined,
    };
  });
}

export type FirmsResult = {
  hotspots: Hotspot[];
  source: "firms" | "sample";
};

// Shared by /api/hotspots (map display) and the alert cron job (danger-point
// source), so there's one place that knows how to talk to FIRMS.
export async function fetchFirmsHotspots(bbox: string = DEFAULT_BBOX): Promise<FirmsResult> {
  const mapKey = process.env.NASA_FIRMS_MAP_KEY;
  if (!mapKey) {
    return { hotspots: SAMPLE_HOTSPOTS, source: "sample" };
  }

  const url = `https://firms.modaps.eosdis.nasa.gov/api/area/csv/${mapKey}/${FIRMS_SOURCE}/${bbox}/${DAY_RANGE}`;

  try {
    const response = await fetch(url, { next: { revalidate: 900 } });
    if (!response.ok) {
      throw new Error(`FIRMS responded ${response.status}`);
    }
    const csv = await response.text();
    return { hotspots: parseFirmsCsv(csv), source: "firms" };
  } catch (err) {
    console.error("Failed to fetch FIRMS data, falling back to sample:", err);
    return { hotspots: SAMPLE_HOTSPOTS, source: "sample" };
  }
}
