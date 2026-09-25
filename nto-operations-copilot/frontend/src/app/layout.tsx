import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NTO Operations Copilot",
  description:
    "Source-grounded AI operations intelligence for NTO research, preparation and quality control.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}