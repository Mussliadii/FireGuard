import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FireGuard AI — Wildfire Detection & Early Warning",
  description:
    "Dashboard for early detection, risk prediction, and real-time wildfire alerts.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
