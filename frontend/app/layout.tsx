import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LucidLaw — Plain-language legal guidance",
  description:
    "Describe a legal situation in plain language and get a clear, supportive first step.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-AU">
      <body>{children}</body>
    </html>
  );
}
