import { prisma } from "@/lib/prisma";
import { getResend, EMAIL_FROM } from "@/lib/resend";

/**
 * Inbound Email Notification System
 * 
 * Notifies team members when a creator/contact replies to an email.
 * Respects user notification preferences (notifyInboundEmail).
 * 
 * Call this fire-and-forget from webhook handler:
 *   notifyTeamOfInboundMessage({ ... }).catch(() => {});
 */

interface NotificationInput {
  teamId: string;
  creatorName: string | null;
  creatorEmail: string;
  subject: string | null;
  body: string | null;
  attachments: { filename: string; size: number | null }[];
  threadId: string;
  creatorId?: string;
}

export async function notifyTeamOfInboundMessage({
  teamId,
  creatorName,
  creatorEmail,
  subject,
  body,
  attachments,
  threadId,
  creatorId,
}: NotificationInput): Promise<void> {
  // Get team with members who have notifications enabled
  const team = await prisma.team.findUnique({
    where: { id: teamId },
    select: {
      name: true,
      members: {
        include: {
          user: {
            select: {
              id: true,
              email: true,
              name: true,
              notifyInboundEmail: true,
            },
          },
        },
      },
    },
  });

  if (!team) return;

  // Get creator if we have an ID (for assignee check)
  const creator = creatorId
    ? await prisma.creator.findUnique({
        where: { id: creatorId },
        select: { outreachAssigneeId: true },
      })
    : null;

  // Filter to only members with notifications enabled
  let membersToNotify = team.members.filter(
    (member) => member.user.notifyInboundEmail
  );

  // If creator has an assignee, only notify them (if they have notifications enabled)
  if (creator?.outreachAssigneeId) {
    const assignee = membersToNotify.find(m => m.id === creator.outreachAssigneeId);
    if (assignee) {
      membersToNotify = [assignee];
    }
    // If assignee doesn't have notifications enabled, fall back to all members
  }

  if (membersToNotify.length === 0) return;

  const resend = getResend();
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || "https://app.example.com";
  const threadUrl = `${appUrl}/teams/${teamId}/inbox?thread=${threadId}`;
  const senderDisplay = creatorName ? `${creatorName} (${creatorEmail})` : creatorEmail;

  // Send notification to each member
  await Promise.all(
    membersToNotify.map(async (member) => {
      const recipientName = member.user.name || "there";

      const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin: 0; padding: 0; background-color: #fafafa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fafafa;">
    <tr>
      <td align="center" style="padding: 48px 20px;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 480px; background-color: #ffffff; border: 1px solid #e5e5e5; border-radius: 4px;">
          <tr>
            <td style="padding: 40px 40px 32px 40px;">
              <p style="margin: 0 0 24px 0; font-size: 13px; font-weight: 500; color: #666; letter-spacing: 0.02em; text-transform: uppercase;">
                New reply in inbox
              </p>
              
              <p style="margin: 0 0 20px 0; font-size: 15px; line-height: 1.6; color: #0a0a0a;">
                Hi ${escapeHtml(recipientName)},
              </p>
              
              <p style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.6; color: #0a0a0a;">
                <strong style="font-weight: 600;">${escapeHtml(senderDisplay)}</strong> replied to a conversation in <strong style="font-weight: 600;">${escapeHtml(team.name)}</strong>.
              </p>
              
              ${subject ? `
              <div style="padding: 16px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 4px; margin-bottom: 16px;">
                <p style="margin: 0 0 4px 0; font-size: 12px; color: #666; font-weight: 500;">Subject</p>
                <p style="margin: 0; font-size: 14px; color: #0a0a0a; line-height: 1.5;">${escapeHtml(subject)}</p>
              </div>
              ` : ""}
              
              ${body ? `
              <div style="padding: 16px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 4px; margin-bottom: 16px;">
                <p style="margin: 0 0 4px 0; font-size: 12px; color: #666; font-weight: 500;">Message</p>
                <p style="margin: 0; font-size: 14px; color: #0a0a0a; line-height: 1.5; white-space: pre-wrap;">${escapeHtml(body.length > 500 ? body.slice(0, 500) + "..." : body)}</p>
              </div>
              ` : ""}
              
              ${attachments.length > 0 ? `
              <div style="padding: 16px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 4px; margin-bottom: 24px;">
                <p style="margin: 0 0 8px 0; font-size: 12px; color: #666; font-weight: 500;">Attachments (${attachments.length})</p>
                ${attachments.map(att => `
                <p style="margin: 0 0 4px 0; font-size: 13px; color: #0a0a0a;">📎 ${escapeHtml(att.filename)} ${att.size ? `<span style="color: #666; font-size: 12px;">(${formatFileSize(att.size)})</span>` : ""}</p>
                `).join("")}
              </div>
              ` : ""}
              
              <a href="${threadUrl}" style="display: inline-block; background-color: #0a0a0a; color: #ffffff; padding: 10px 16px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 13px;">
                View conversation
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding: 24px 40px; border-top: 1px solid #e5e5e5;">
              <p style="margin: 0; font-size: 12px; line-height: 1.6; color: #999;">
                You're receiving this because you have email notifications enabled.
                <a href="${appUrl}/teams/${teamId}/settings?section=notifications" style="color: #666; text-decoration: underline;">Manage preferences</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

      await resend.emails.send({
        from: EMAIL_FROM,
        to: member.user.email,
        subject: `New reply from ${senderDisplay}`,
        html: htmlContent,
      });
    })
  );
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
