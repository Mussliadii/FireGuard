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

  const formData = await req.formData();
  const file = formData.get("file");
  if (!(file instanceof Blob)) {
    return NextResponse.json({ error: "field 'file' is required" }, { status: 400 });
  }

  const upstream = new FormData();
  upstream.set("file", file, (file as File).name ?? "upload.jpg");

  const response = await fetch(`${backendUrl}/detect`, {
    method: "POST",
    body: upstream,
  });

  const body = await response.json();
  return NextResponse.json(body, { status: response.status });
}
