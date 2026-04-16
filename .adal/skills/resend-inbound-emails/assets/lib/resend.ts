import { Resend } from "resend";
import { prisma } from "@/lib/prisma";

/**
 * Resend Email Client with Address Building Utilities
 * 
 * Key concepts:
 * - FROM address: User's email prefix @ their selected domain (or default)
 * - REPLY-TO: Always uses default inbound domain for tracking
 */

let resendInstance: Resend | null = null;

export function getResend(): Resend {
  if (!resendInstance) {
    const apiKey = process.env.RESEND_API_KEY;
    if (!apiKey) {
      throw new Error("RESEND_API_KEY environment variable is not set");
    }
    resendInstance = new Resend(apiKey);
  }
  return resendInstance;
}

// Default sender for system emails
export const EMAIL_FROM = process.env.EMAIL_FROM || "noreply@example.com";

// Your inbound domain for receiving emails
// All reply-to addresses use this domain
export const DEFAULT_EMAIL_DOMAIN = process.env.DEFAULT_EMAIL_DOMAIN || "inbox.yourdomain.com";

/**
 * Build a "from" address using the user's email prefix on the specified domain.
 * 
 * @example
 * buildFromAddress("kai@gmail.com", "Kai Chen", "acme.com")
 * // Returns: "Kai Chen <kai@acme.com>"
 */
export function buildFromAddress(
  userEmail: string | null | undefined,
  displayName?: string | null,
  domain: string = DEFAULT_EMAIL_DOMAIN
): string {
  const prefix = userEmail?.split("@")[0] ?? "inbox";
  const address = `${prefix}@${domain}`;
  return displayName ? `${displayName} <${address}>` : address;
}

/**
 * Build a reply-to address that always uses the default inbound domain.
 * This ensures all replies are tracked in the inbox system.
 * 
 * @example
 * buildReplyToAddress("kai@gmail.com")
 * // Returns: "kai@inbox.yourdomain.com"
 */
export function buildReplyToAddress(userEmail: string | null | undefined): string {
  const prefix = userEmail?.split("@")[0] ?? "inbox";
  return `${prefix}@${DEFAULT_EMAIL_DOMAIN}`;
}

/**
 * Get the user's preferred sending domain.
 * Falls back to default if user hasn't set one or their domain is invalid.
 */
export async function getUserSendingDomain(userId: string, teamId: string): Promise<string> {
  // Get user's preference
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: { sendFromDomain: true }
  });
  
  // If user has a preference, validate it's a verified domain for this team
  if (user?.sendFromDomain) {
    const validDomain = await prisma.teamDomain.findFirst({
      where: { 
        teamId, 
        domain: user.sendFromDomain,
        status: "verified" 
      }
    });
    if (validDomain) {
      return user.sendFromDomain;
    }
  }
  
  return DEFAULT_EMAIL_DOMAIN;
}

/**
 * Get the team's active custom sending domain, or fall back to default.
 */
export async function getTeamSendingDomain(teamId: string): Promise<string> {
  const activeDomain = await prisma.teamDomain.findFirst({
    where: { teamId, isActive: true, status: "verified" },
  });
  return activeDomain?.domain ?? DEFAULT_EMAIL_DOMAIN;
}
