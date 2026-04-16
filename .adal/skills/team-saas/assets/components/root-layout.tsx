import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { Providers } from "@/components/providers";
import "./globals.css";

/**
 * Root Layout Template
 * 
 * File: src/app/layout.tsx
 * 
 * Features:
 * - Geist fonts (sans + mono) from Vercel
 * - Providers wrapper for theme, session, query, tooltips
 * - Antialiased text rendering
 * - suppressHydrationWarning for next-themes
 */

export const metadata: Metadata = {
  title: "My SaaS",
  description: "Description of your SaaS product",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${GeistSans.variable} ${GeistMono.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
