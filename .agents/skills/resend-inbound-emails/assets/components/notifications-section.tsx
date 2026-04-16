"use client";

import { Bell, Mail } from "lucide-react";
import { toast } from "sonner";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useUserProfile, useUpdateUserProfile } from "@/hooks/use-user";

/**
 * Notifications Section Component
 * 
 * User settings section for managing notification preferences.
 * Toggle to enable/disable email notifications for inbound inbox replies.
 */

export function NotificationsSection() {
  const { data: user, isLoading } = useUserProfile();
  const updateUser = useUpdateUserProfile();

  async function handleNotificationToggle(checked: boolean) {
    try {
      await updateUser.mutateAsync({ notifyInboundEmail: checked });
      toast.success(
        checked
          ? "Email notifications enabled"
          : "Email notifications disabled"
      );
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to update notification settings"
      );
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!user) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Notifications
        </CardTitle>
        <CardDescription>
          Configure how you receive notifications
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-start gap-3">
            <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
            <div className="space-y-0.5">
              <Label htmlFor="notify-inbound" className="text-sm font-medium">
                Inbox reply notifications
              </Label>
              <p className="text-sm text-muted-foreground">
                Receive an email when someone replies to your inbox messages
              </p>
            </div>
          </div>
          <Switch
            id="notify-inbound"
            checked={user.notifyInboundEmail}
            onCheckedChange={handleNotificationToggle}
            disabled={updateUser.isPending}
          />
        </div>
      </CardContent>
    </Card>
  );
}
