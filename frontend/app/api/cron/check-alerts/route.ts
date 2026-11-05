import { NextRequest, NextResponse } from "next/server";
import { getSupabaseAdmin } from "@/lib/supabase";
import { haversineDistanceKm } from "@/lib/geo";
import { sendDangerAlert } from "@/lib/webpush";
import { fetchFirmsHotspots } from "@/lib/firms";
import { fetchCurrentWeather } from "@/lib/weather";
import { MONITORED_LOCATIONS } from "@/lib/monitored-locations";

const ALERT_RADIUS_KM = 10;

type DangerPoint = {
  lat: number;
  lon: number;
  risk: "medium" | "high";
  source: "detection" | "prediction" | "firms";
};

// Already-ignited fires the satellite picked up on its own — no one has to
// upload a photo or pick a point for this source to fire.
async function getFirmsDangerPoints(): Promise<DangerPoint[]> {
  const { hotspots } = await fetchFirmsHotspots();
  return hotspots
    .filter((h) => h.risk !== "low")
    .map((h) => ({
      lat: h.lat,
      lon: h.lon,
      risk: h.risk as "medium" | "high",
      source: "firms" as const,
    }));
}

// Runs the risk model against current weather for a fixed set of fire-prone
// regions, on a schedule. This is what makes risk prediction preventive
// instead of a manual, one-point-at-a-time lookup tool.
async function getPredictionDangerPoints(): Promise<DangerPoint[]> {
  const backendUrl = process.env.BACKEND_INFERENCE_URL;
  if (!backendUrl) return [];

  const checks = await Promise.allSettled(
    MONITORED_LOCATIONS.map(async (loc) => {
      const weather = await fetchCurrentWeather(loc.lat, loc.lon);
      const response = await fetch(`${backendUrl}/predict-risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: loc.lat,
          lon: loc.lon,
          temperature_c: weather.temperatureC,
          humidity_pct: weather.humidityPct,
          rainfall_mm: weather.rainfallMm,
          wind_speed_kmh: weather.windSpeedKmh,
        }),
      });
      if (!response.ok) {
        throw new Error(`predict-risk responded ${response.status} for ${loc.name}`);
      }
      return { loc, result: await response.json() };
    })
  );

  const dangerPoints: DangerPoint[] = [];
  for (const check of checks) {
    if (check.status === "rejected") {
      console.error("Risk prediction failed for a monitored location:", check.reason);
      continue;
    }
    const { loc, result } = check.value;
    if (result.risk_label === "medium" || result.risk_label === "high") {
      dangerPoints.push({ lat: loc.lat, lon: loc.lon, risk: result.risk_label, source: "prediction" });
    }
  }
  return dangerPoints;
}

async function getCurrentDangerPoints(): Promise<DangerPoint[]> {
  const [firmsPoints, predictionPoints] = await Promise.all([
    getFirmsDangerPoints(),
    getPredictionDangerPoints(),
  ]);
  return [...firmsPoints, ...predictionPoints];
}

// Vercel Cron calls this endpoint on the schedule in vercel.json.
// Protected by an Authorization header so it can't be triggered publicly.
export async function GET(req: NextRequest) {
  const auth = req.headers.get("authorization");
  if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const dangerPoints = await getCurrentDangerPoints();
  if (dangerPoints.length === 0) {
    return NextResponse.json({ alerted: 0, reason: "no danger points" });
  }

  const supabase = getSupabaseAdmin();
  const { data: subscribers, error } = await supabase
    .from("subscribers")
    .select("id, lat, lon, push_subscription");

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  let alerted = 0;

  for (const point of dangerPoints) {
    for (const sub of subscribers ?? []) {
      const distance = haversineDistanceKm(
        point.lat,
        point.lon,
        sub.lat,
        sub.lon
      );
      if (distance > ALERT_RADIUS_KM) continue;

      try {
        await sendDangerAlert(sub.push_subscription, {
          title: "⚠️ Wildfire Alert",
          body: `${point.risk} risk detected ${distance.toFixed(
            1
          )} km from your location (source: ${point.source}).`,
          risk: point.risk,
          lat: point.lat,
          lon: point.lon,
        });
        alerted += 1;
      } catch (err) {
        console.error("Failed to send push to", sub.id, err);
      }
    }
  }

  return NextResponse.json({ alerted, danger_points: dangerPoints.length });
}
