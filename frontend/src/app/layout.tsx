import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Crisis AI Platform — Autonomous Disaster Logistics",
  description: "AI-Driven Crisis Resource Intelligence & Autonomous Decision Loop",
  manifest: "/manifest.json",
};

import OfflineSync from "@/components/OfflineSync";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full dark">
      <body className={`${inter.className} min-h-screen bg-slate-950 text-slate-100 antialiased`}>
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-slate-900 focus:rounded-lg focus:shadow-lg">Skip to main content</a>
        <AuthProvider>
          <OfflineSync />
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
