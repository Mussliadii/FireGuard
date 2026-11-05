import { NextRequest, NextResponse } from "next/server";
import { getSupabaseAdmin } from "@/lib/supabase";

// Body: { lat: number, lon: number, push_subscription: PushSubscriptionJSON }
export async function POST(req: NextRequest) {
  const body = await req.json();
  const { lat, lon, push_subscription } = body;

  if (typeof lat !== "number" || typeof lon !== "number" || !push_subscription) {
    return NextResponse.json(
      { error: "lat, lon, and push_subscription are required" },
      { status: 400 }
    );
  }

  const supabase = getSupabaseAdmin();
  const { data, error } = await supabase
    .from("subscribers")
    .insert({ lat, lon, push_subscription })
    .select("id")
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ id: data.id });
}
