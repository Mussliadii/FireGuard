import { createClient } from "@supabase/supabase-js";

// Used in API routes (server-side) with the service role key so it can
// read/write the subscribers table without row-level security restrictions.
export function getSupabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !serviceKey) {
    throw new Error(
      "Supabase env vars are not set (NEXT_PUBLIC_SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY)"
    );
  }

  return createClient(url, serviceKey);
}

/*
 * Expected table schema (create via the Supabase SQL editor):
 *
 * create table subscribers (
 *   id uuid primary key default gen_random_uuid(),
 *   lat double precision not null,
 *   lon double precision not null,
 *   push_subscription jsonb not null,
 *   created_at timestamptz default now()
 * );
 */
