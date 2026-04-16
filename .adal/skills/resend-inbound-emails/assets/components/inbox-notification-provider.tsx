"use client";

import { useParams } from "next/navigation";
import { useInboxPolling } from "@/hooks/use-inbox-polling";

/**
 * Inbox Notification Provider
 * 
 * Wrapper component that enables inbox polling for toast notifications.
 * Should wrap the dashboard layout to enable notifications on any page.
 * 
 * Usage in dashboard layout:
 * ```tsx
 * export default function DashboardLayout({ children }) {
 *   return (
 *     <InboxNotificationProvider>
 *       <DashboardShell>{children}</DashboardShell>
 *     </InboxNotificationProvider>
 *   );
 * }
 * ```
 */

interface InboxNotificationProviderProps {
  children: React.ReactNode;
}

export function InboxNotificationProvider({
  children,
}: InboxNotificationProviderProps) {
  const params = useParams<{ teamId: string }>();
  const teamId = params?.teamId;

  // Only poll when user has a team context
  useInboxPolling(teamId, {
    interval: 10000, // 10 seconds
    enabled: !!teamId,
  });

  return <>{children}</>;
}
