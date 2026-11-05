"use client";

import { useEffect, useRef, useState } from "react";

type Detection = {
  label: string;
  confidence: number;
  bbox: [number, number, number, number];
};

type DetectResult = {
  detections: Detection[];
  is_danger: boolean;
  max_confidence: number;
};

const BOX_COLOR: Record<string, string> = {
  fire: "#e37f7f",
  smoke: "#e3d57f",
};

export default function DetectForm() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [result, setResult] = useState<DetectResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const imgRef = useRef<HTMLImageElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    setFile(selected);
    setResult(null);
    setError("");
    setPreviewUrl(selected ? URL.createObjectURL(selected) : "");
  }

  async function handleSubmit() {
    if (!file) {
      setError("Choose an image first");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.set("file", file);

      const response = await fetch("/api/detect", { method: "POST", body: formData });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error ?? "Detection failed");
      setResult(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function drawBoxes() {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    if (!img || !canvas || !result) return;

    canvas.width = img.clientWidth;
    canvas.height = img.clientHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const scaleX = img.clientWidth / img.naturalWidth;
    const scaleY = img.clientHeight / img.naturalHeight;

    for (const det of result.detections) {
      const [x1, y1, x2, y2] = det.bbox;
      const color = BOX_COLOR[det.label] ?? "#e37f7f";
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(x1 * scaleX, y1 * scaleY, (x2 - x1) * scaleX, (y2 - y1) * scaleY);
      ctx.fillStyle = color;
      ctx.font = "14px sans-serif";
      ctx.fillText(
        `${det.label} ${(det.confidence * 100).toFixed(0)}%`,
        x1 * scaleX,
        Math.max(0, y1 * scaleY - 4)
      );
    }
  }

  useEffect(() => {
    drawBoxes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result]);

  return (
    <div>
      <div className="form-row">
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button className="btn-primary" type="button" onClick={handleSubmit} disabled={loading || !file}>
          {loading ? "Processing..." : "Detect"}
        </button>
      </div>

      {error && <p className="text-error">{error}</p>}

      {previewUrl && (
        <div className="preview-frame">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            ref={imgRef}
            src={previewUrl}
            alt="Uploaded preview"
            onLoad={drawBoxes}
            style={{ maxWidth: "100%", maxHeight: 400, display: "block" }}
          />
          <canvas
            ref={canvasRef}
            style={{ position: "absolute", top: 0, left: 0, pointerEvents: "none" }}
          />
        </div>
      )}

      {result && (
        <div className="result-panel">
          <span className={`badge ${result.is_danger ? "badge-high" : "badge-low"}`}>
            {result.is_danger ? "DANGER DETECTED" : "CLEAR"}
          </span>{" "}
          max confidence {(result.max_confidence * 100).toFixed(1)}%
          <ul>
            {result.detections.map((det, i) => (
              <li key={i}>
                {det.label} — {(det.confidence * 100).toFixed(1)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
