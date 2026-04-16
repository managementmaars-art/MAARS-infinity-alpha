"use client";

import { Globe, Mail } from "lucide-react";
import { toast } from "sonner";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useUserProfile, useUpdateUserProfile } from "@/hooks/use-user";
import { useAvailableDomains } from "@/hooks/use-available-domains";
import { DEFAULT_EMAIL_DOMAIN } from "@/lib/resend";

/**
 * Email Settings Section Component
 * 
 * User settings section for selecting preferred sending domain.
 * Shows domains from all teams the user belongs to.
 */

export function EmailSettingsSection() {
  const { data: user, isLoading: isLoadingUser } = useUserProfile();
  const { data: domainsData, isLoading: isLoadingDomains } = useAvailableDomains();
  const updateUser = useUpdateUserProfile();

  const isLoading = isLoadingUser || isLoadingDomains;
  const availableDomains = domainsData?.domains ?? [];
  const currentDomain = user?.sendFromDomain;

  async function handleDomainChange(value: string) {
    const newDomain = value === "default" ? null : value;
    try {
      await updateUser.mutateAsync({ sendFromDomain: newDomain });
      toast.success(
        newDomain
          ? `Sending domain set to ${newDomain}`
          : "Using default sending domain"
      );
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to update sending domain"
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
          <Skeleton className="h-10 w-full max-w-md" />
        </CardContent>
      </Card>
    );
  }

  if (!user) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mail className="h-5 w-5" />
          Email Settings
        </CardTitle>
        <CardDescription>
          Configure your email sending preferences
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="sending-domain">Sending Domain</Label>
          <p className="text-sm text-muted-foreground mb-3">
            Choose which domain to send emails from. This affects the &quot;From&quot; address.
          </p>
          
          {availableDomains.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No custom domains available. Using default: {DEFAULT_EMAIL_DOMAIN}
            </p>
          ) : (
            <Select
              value={currentDomain || "default"}
              onValueChange={handleDomainChange}
              disabled={updateUser.isPending}
            >
              <SelectTrigger id="sending-domain" className="w-full max-w-md">
                <SelectValue placeholder="Select a domain" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="default">
                  <span className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    {DEFAULT_EMAIL_DOMAIN}
                    <span className="text-muted-foreground">(default)</span>
                  </span>
                </SelectItem>
                {availableDomains.map((domain) => (
                  <SelectItem key={domain.domain} value={domain.domain}>
                    <span className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      {domain.domain}
                      <span className="text-muted-foreground text-xs">
                        ({domain.teamName})
                      </span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
