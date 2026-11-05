"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { Hotspot, SAMPLE_HOTSPOTS } from "@/lib/hotspots";

const RISK_COLOR: Record<Hotspot["risk"], string> = {
  low: "#7fe3a0",
  medium: "#e3d57f",
  high: "#e37f7f",
};

export default function FireMap() {
  const [hotspots, setHotspots] = useState<Hotspot[]>(SAMPLE_HOTSPOTS);
  const [source, setSource] = useState<"sample" | "firms">("sample");

  useEffect(() => {
    let cancelled = false;

    fetch("/api/hotspots")
      .then((res) => res.json())
      .then((data) => {
        if (cancelled) return;
        setHotspots(data.hotspots ?? SAMPLE_HOTSPOTS);
        setSource(data.source ?? "sample");
      })
      .catch(() => {
        if (!cancelled) setSource("sample");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <MapContainer
        center={[-1.5, 114.5]}
        zoom={5}
        style={{ height: 400, width: "100%", borderRadius: 12 }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {hotspots.map((h) => (
          <CircleMarker
            key={h.id}
            center={[h.lat, h.lon]}
            radius={8}
            pathOptions={{ color: RISK_COLOR[h.risk], fillOpacity: 0.7 }}
          >
            <Popup>
              Risk: {h.risk} <br />
              Confidence: {(h.confidence * 100).toFixed(0)}%
              {h.acquiredAt && (
                <>
                  <br />
                  Detected: {h.acquiredAt}
                </>
              )}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      {source === "sample" && (
        <p className="text-hint">
          Showing sample data — set <code>NASA_FIRMS_MAP_KEY</code> in the
          environment for real NASA FIRMS hotspot data.
        </p>
      )}
    </div>
  );
}
