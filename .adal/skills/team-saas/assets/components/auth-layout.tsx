"use client";

import Link from "next/link";

/**
 * Auth Layout Template
 * 
 * File: src/app/(auth)/layout.tsx
 * 
 * This is a Client Component for auth pages (login, register, etc.)
 * It provides styling but NO authentication - these are public pages.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header with logo */}
      <header className="flex items-center justify-between p-6">
        <Link href="/" className="flex items-center gap-2">
          {/* Your logo here */}
          <span className="font-semibold">My SaaS</span>
        </Link>
      </header>
      
      {/* Main content */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          {children}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="p-6 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} My SaaS
      </footer>
    </div>
  );
}
