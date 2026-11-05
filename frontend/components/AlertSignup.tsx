"use client";

import { useState } from "react";
import { getCurrentPosition, subscribeToPush } from "@/lib/push";

type Status = "idle" | "loading" | "success" | "error";

export default function AlertSignup() {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState<string>("");

  async function handleSignup() {
    setStatus("loading");
    setMessage("");

    try {
      const position = await getCurrentPosition();
      const subscription = await subscribeToPush();

      const response = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
          push_subscription: subscription.toJSON(),
        }),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.error ?? "Failed to sign up");
      }

      setStatus("success");
      setMessage("Done! You'll be notified about danger near this location.");
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  return (
    <div>
      <button className="btn-primary" onClick={handleSignup} disabled={status === "loading"}>
        {status === "loading" ? "Working..." : "Enable Notifications & Sign Up"}
      </button>
      {message && (
        <p className={status === "error" ? "text-error" : "text-hint"}>{message}</p>
      )}
    </div>
  );
}
