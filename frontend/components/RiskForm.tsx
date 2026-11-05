"use client";

import { useState } from "react";
import { fetchCurrentWeather } from "@/lib/weather";
import { getCurrentPosition } from "@/lib/push";

type RiskResult = {
  risk_score: number;
  risk_label: "low" | "medium" | "high";
  model: string;
};

export default function RiskForm() {
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [temperature, setTemperature] = useState("");
  const [humidity, setHumidity] = useState("");
  const [rainfall, setRainfall] = useState("");
  const [windSpeed, setWindSpeed] = useState("");
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [loadingPredict, setLoadingPredict] = useState(false);
  const [result, setResult] = useState<RiskResult | null>(null);
  const [error, setError] = useState("");

  async function handleUseMyLocation() {
    try {
      const position = await getCurrentPosition();
      setLat(String(position.coords.latitude));
      setLon(String(position.coords.longitude));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get location");
    }
  }

  async function handleFetchWeather() {
    setError("");
    if (!lat || !lon) {
      setError("Fill in lat/lon first, or use the my-location button");
      return;
    }
    setLoadingWeather(true);
    try {
      const weather = await fetchCurrentWeather(parseFloat(lat), parseFloat(lon));
      setTemperature(String(weather.temperatureC));
      setHumidity(String(weather.humidityPct));
      setRainfall(String(weather.rainfallMm));
      setWindSpeed(String(weather.windSpeedKmh));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch weather");
    } finally {
      setLoadingWeather(false);
    }
  }

  async function handlePredict() {
    setError("");
    setResult(null);
    setLoadingPredict(true);
    try {
      const response = await fetch("/api/predict-risk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: parseFloat(lat || "0"),
          lon: parseFloat(lon || "0"),
          temperature_c: parseFloat(temperature || "0"),
          humidity_pct: parseFloat(humidity || "0"),
          rainfall_mm: parseFloat(rainfall || "0"),
          wind_speed_kmh: parseFloat(windSpeed || "0"),
        }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error ?? "Failed to predict risk");
      setResult(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoadingPredict(false);
    }
  }

  return (
    <div>
      <div className="form-row">
        <input placeholder="Latitude" value={lat} onChange={(e) => setLat(e.target.value)} />
        <input placeholder="Longitude" value={lon} onChange={(e) => setLon(e.target.value)} />
        <button type="button" onClick={handleUseMyLocation}>
          Use My Location
        </button>
      </div>

      <div className="form-row">
        <input
          placeholder="Temperature (°C)"
          value={temperature}
          onChange={(e) => setTemperature(e.target.value)}
        />
        <input
          placeholder="Humidity (%)"
          value={humidity}
          onChange={(e) => setHumidity(e.target.value)}
        />
        <input
          placeholder="Rainfall (mm)"
          value={rainfall}
          onChange={(e) => setRainfall(e.target.value)}
        />
        <input
          placeholder="Wind speed (km/h)"
          value={windSpeed}
          onChange={(e) => setWindSpeed(e.target.value)}
        />
        <button type="button" onClick={handleFetchWeather} disabled={loadingWeather}>
          {loadingWeather ? "Fetching..." : "Auto-fetch Weather"}
        </button>
      </div>

      <button className="btn-primary" type="button" onClick={handlePredict} disabled={loadingPredict}>
        {loadingPredict ? "Predicting..." : "Predict Risk"}
      </button>

      {error && <p className="text-error">{error}</p>}

      {result && (
        <div className="result-panel">
          <span className={`badge badge-${result.risk_label}`}>
            {result.risk_label.toUpperCase()}
          </span>{" "}
          score {(result.risk_score * 100).toFixed(1)}%
        </div>
      )}
    </div>
  );
}
