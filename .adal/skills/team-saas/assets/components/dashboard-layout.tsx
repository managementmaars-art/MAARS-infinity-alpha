import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { DashboardShell } from "./dashboard-shell";

/**
 * Dashboard Layout Template
 * 
 * File: src/app/(dashboard)/layout.tsx
 * 
 * This is a Server Component that:
 * 1. Checks authentication server-side using auth()
 * 2. Redirects to /login if no session
 * 3. Passes session to DashboardShell
 * 
 * This is the primary route protection mechanism - NOT middleware.
 */
export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Server-side auth check
  const session = await auth();

  if (!session?.user) {
    redirect("/login");
  }

  return <DashboardShell session={session}>{children}</DashboardShell>;
}
