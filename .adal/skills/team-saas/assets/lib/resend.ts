import { Resend } from "resend";

/**
 * Resend email client with lazy initialization
 * 
 * Usage:
 *   const resend = getResend();
 *   await resend.emails.send({ from, to, subject, html });
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

// Default email sender address
export const EMAIL_FROM = process.env.EMAIL_FROM || "noreply@example.com";

// Default email domain for custom sending
export const DEFAULT_EMAIL_DOMAIN = "yourdomain.com";

/**
 * Build a "from" address using display name and domain
 * e.g., buildFromAddress("kai@example.com", "Kai") → "Kai <kai@yourdomain.com>"
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
 * Build a reply-to address
 */
export function buildReplyToAddress(userEmail: string | null | undefined): string {
  const prefix = userEmail?.split("@")[0] ?? "inbox";
  return `${prefix}@${DEFAULT_EMAIL_DOMAIN}`;
}

// ===========================================
// Email Templates
// ===========================================

/**
 * Send a team invitation email
 */
export async function sendInvitationEmail({
  to,
  inviterName,
  teamName,
  inviteUrl,
}: {
  to: string;
  inviterName: string;
  teamName: string;
  inviteUrl: string;
}) {
  const resend = getResend();
  
  return resend.emails.send({
    from: EMAIL_FROM,
    to,
    subject: `You're invited to join ${teamName}`,
    html: `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <h1 style="font-size: 24px; font-weight: 600; margin-bottom: 24px;">
          Join ${teamName}
        </h1>
        <p style="font-size: 16px; color: #374151; margin-bottom: 16px;">
          ${inviterName} has invited you to join <strong>${teamName}</strong>.
        </p>
        <a href="${inviteUrl}" 
           style="display: inline-block; background-color: #8b5cf6; color: white; 
                  padding: 12px 24px; border-radius: 8px; text-decoration: none;
                  font-weight: 500; margin: 24px 0;">
          Accept Invitation
        </a>
        <p style="font-size: 14px; color: #6b7280; margin-top: 24px;">
          This invitation expires in 7 days.
        </p>
      </div>
    `,
    text: `${inviterName} has invited you to join ${teamName}. Accept the invitation: ${inviteUrl}`,
  });
}

/**
 * Send a password reset email
 */
export async function sendPasswordResetEmail({
  to,
  resetUrl,
}: {
  to: string;
  resetUrl: string;
}) {
  const resend = getResend();
  
  return resend.emails.send({
    from: EMAIL_FROM,
    to,
    subject: "Reset your password",
    html: `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <h1 style="font-size: 24px; font-weight: 600; margin-bottom: 24px;">
          Reset your password
        </h1>
        <p style="font-size: 16px; color: #374151; margin-bottom: 16px;">
          Click the button below to reset your password.
        </p>
        <a href="${resetUrl}" 
           style="display: inline-block; background-color: #8b5cf6; color: white; 
                  padding: 12px 24px; border-radius: 8px; text-decoration: none;
                  font-weight: 500; margin: 24px 0;">
          Reset Password
        </a>
        <p style="font-size: 14px; color: #6b7280; margin-top: 24px;">
          If you didn't request this, you can safely ignore this email.
          This link expires in 1 hour.
        </p>
      </div>
    `,
    text: `Reset your password: ${resetUrl}`,
  });
}
