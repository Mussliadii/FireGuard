import { NextRequest, NextResponse } from "next/server";
import { DEFAULT_BBOX } from "@/lib/hotspots";
import { fetchFirmsHotspots } from "@/lib/firms";

export async function GET(req: NextRequest) {
  const bbox = req.nextUrl.searchParams.get("bbox") ?? DEFAULT_BBOX;
  const { hotspots, source } = await fetchFirmsHotspots(bbox);
  return NextResponse.json({ hotspots, source });
}
