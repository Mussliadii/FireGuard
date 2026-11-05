import { NextRequest, NextResponse } from "next/server";

// Proxies to the FastAPI inference backend so BACKEND_INFERENCE_URL stays a
// server-only secret and the browser never needs CORS access to it directly.
export async function POST(req: NextRequest) {
  const backendUrl = process.env.BACKEND_INFERENCE_URL;
  if (!backendUrl) {
    return NextResponse.json(
      { error: "BACKEND_INFERENCE_URL is not set" },
      { status: 500 }
    );
  }

  const payload = await req.json();

  const response = await fetch(`${backendUrl}/predict-risk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const body = await response.json();
  return NextResponse.json(body, { status: response.status });
}
