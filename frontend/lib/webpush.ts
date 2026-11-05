import webpush from "web-push";

let configured = false;

export function getWebPush() {
  if (!configured) {
    const publicKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
    const privateKey = process.env.VAPID_PRIVATE_KEY;
    const subject = process.env.VAPID_SUBJECT ?? "mailto:admin@example.com";

    if (!publicKey || !privateKey) {
      throw new Error(
        "VAPID keys are not set. Generate with: npx web-push generate-vapid-keys"
      );
    }

    webpush.setVapidDetails(subject, publicKey, privateKey);
    configured = true;
  }

  return webpush;
}

export type DangerAlert = {
  title: string;
  body: string;
  risk: "medium" | "high";
  lat: number;
  lon: number;
};

export async function sendDangerAlert(
  subscription: webpush.PushSubscription,
  alert: DangerAlert
) {
  const client = getWebPush();
  return client.sendNotification(subscription, JSON.stringify(alert));
}
