import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getResend, DEFAULT_EMAIL_DOMAIN } from "@/lib/resend";
import {
  parseMessageIdHeader,
  parseReferencesHeader,
  getHeaderValue,
} from "@/lib/inbox/email-headers";
import { findThreadByHeaders, findOrCreateCreatorThread } from "@/lib/inbox/threading";
import { parseReplyContent } from "@/lib/inbox/reply-parser";
import { notifyTeamOfInboundMessage } from "@/lib/inbox/inbound-notification";

/**
 * Resend Webhook Handler
 * 
 * File: src/app/api/webhooks/resend/route.ts
 * 
 * Handles:
 * - email.received: Process inbound emails (both INBOUND from external and OUTBOUND from team)
 * - email.sent/delivered/bounced: Update delivery status
 * 
 * Configure in Resend Dashboard:
 * - URL: https://yourdomain.com/api/webhooks/resend
 * - Events: email.received, email.delivered, email.bounced, email.sent
 * 
 * Inbound Matching Priority:
 * 1. RFC 5322 headers (Message-ID, In-Reply-To, References)
 * 2. Creator.email (primary email)
 * 3. CreatorContact.email (associated contacts)
 * 4. Domain matching (creator with same email domain)
 * 5. Auto-create new creator
 */

// Resend webhook event types
interface ResendWebhookEvent {
  type: string;
  data: Record<string, unknown>;
}

export async function POST(req: NextRequest) {
  const payload = await req.text();
  const resend = getResend();

  // Verify webhook signature
  let event: ResendWebhookEvent;
  try {
    event = resend.webhooks.verify({
      payload,
      headers: {
        id: req.headers.get("svix-id") ?? "",
        timestamp: req.headers.get("svix-timestamp") ?? "",
        signature: req.headers.get("svix-signature") ?? "",
      },
      webhookSecret: process.env.RESEND_WEBHOOK_SECRET ?? "",
    }) as unknown as ResendWebhookEvent;
  } catch {
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  const eventType = event.type;
  const eventData = event.data;

  // Handle inbound email
  if (eventType === "email.received") {
    return handleInboundEmail(event, resend);
  }

  // Handle delivery status updates
  if (["email.sent", "email.delivered", "email.bounced"].includes(eventType)) {
    return handleDeliveryStatus(event);
  }

  return NextResponse.json({ ok: true });
}

// ===========================================
// Inbound Email Handler
// ===========================================

async function handleInboundEmail(event: ResendWebhookEvent, resend: ReturnType<typeof getResend>) {
  const eventData = event.data;
  const resendEmailId = eventData.email_id as string | undefined;
  
  if (!resendEmailId) {
    return NextResponse.json({ ok: true });
  }

  // Deduplication: Check if we've already processed this email
  const existingMessage = await prisma.inboxMessage.findFirst({
    where: { resendEmailId },
  });
  if (existingMessage) {
    return NextResponse.json({ ok: true, duplicate: true });
  }

  // Fetch full email from Resend
  const emailResponse = await resend.emails.receiving.get(resendEmailId);
  const emailData = ((emailResponse as unknown) as { data?: Record<string, unknown> }).data ?? {};

  // Extract email metadata
  const from = emailData.from as string;
  const to = emailData.to as string | string[];
  const cc = emailData.cc as string | string[] | undefined;
  const subject = typeof emailData.subject === "string" ? emailData.subject : null;
  const textBody = emailData.text as string | undefined;
  const htmlBody = emailData.html as string | undefined;

  // Parse RFC 5322 headers for threading
  const headers = (emailData as { headers?: unknown }).headers;
  const messageId = parseMessageIdHeader(getHeaderValue(headers, "message-id"));
  const inReplyTo = parseMessageIdHeader(getHeaderValue(headers, "in-reply-to"));
  const references = parseReferencesHeader(getHeaderValue(headers, "references"));

  // Extract sender email
  const senderEmail = extractEmail(from);
  if (!senderEmail) {
    return NextResponse.json({ error: "Invalid sender" }, { status: 400 });
  }

  // Determine which team this email is for
  // Emails are sent to *@your-inbound-domain.com
  const toAddresses = Array.isArray(to) ? to : [to];
  const ccAddresses = cc ? (Array.isArray(cc) ? cc : [cc]) : [];
  const allRecipients = [...toAddresses, ...ccAddresses];
  
  const team = await resolveTeamFromRecipients(allRecipients);
  if (!team) {
    return NextResponse.json({ error: "Unknown recipient" }, { status: 400 });
  }

  // Check if sender is a team member (OUTBOUND detection)
  const teamMember = await findTeamMemberByEmail(senderEmail, team.id);
  const externalRecipients = filterExternalRecipients(toAddresses);
  const isOutbound = teamMember && externalRecipients.length > 0;

  // Strip quoted content from reply
  const parsedContent = parseReplyContent(textBody, htmlBody);

  if (isOutbound) {
    // OUTBOUND: Team member sending from external email client
    // Find the creator from the external recipients
    const recipientEmail = extractEmail(externalRecipients[0]);
    if (!recipientEmail) {
      return NextResponse.json({ ok: true });
    }

    const creator = await resolveOrCreateCreator(recipientEmail, team.id, null);
    const thread = await findOrCreateCreatorThread({
      teamId: team.id,
      creatorId: creator.id,
      primaryEmail: recipientEmail,
      messageId,
      inReplyTo,
      references,
    });

    const message = await prisma.inboxMessage.create({
      data: {
        threadId: thread.id,
        direction: "OUTBOUND",
        from: senderEmail,
        to: recipientEmail,
        subject,
        textBody: parsedContent.textBody,
        htmlBody: parsedContent.htmlBody,
        resendEmailId,
        messageId,
        inReplyTo,
        references,
        sentAt: new Date(),
        deliveryStatus: "DELIVERED",
      },
    });

    await prisma.inboxThread.update({
      where: { id: thread.id },
      data: { lastMessageAt: new Date(), isRead: true },
    });

    return NextResponse.json({ ok: true, messageId: message.id, direction: "OUTBOUND" });
  }

  // INBOUND: External sender to team inbox
  // Resolve creator using priority matching
  let creator = await resolveCreatorFromEmail(senderEmail, team.id);
  
  // Auto-create if no match
  if (!creator) {
    creator = await prisma.creator.create({
      data: {
        teamId: team.id,
        email: senderEmail,
        name: extractName(from),
        outreachStatus: "IN_CONVERSATION",
      },
      select: { id: true, name: true, email: true },
    });
  }

  // Find or create thread
  const thread = await findOrCreateCreatorThread({
    teamId: team.id,
    creatorId: creator.id,
    primaryEmail: senderEmail,
    messageId,
    inReplyTo,
    references,
  });

  // Create inbox message
  const message = await prisma.inboxMessage.create({
    data: {
      threadId: thread.id,
      direction: "INBOUND",
      from: senderEmail,
      to: toAddresses.join(", "),
      subject,
      textBody: parsedContent.textBody,
      htmlBody: parsedContent.htmlBody,
      resendEmailId,
      messageId,
      inReplyTo,
      references,
      receivedAt: new Date(),
      deliveryStatus: "DELIVERED",
    },
  });

  // Update thread
  await prisma.inboxThread.update({
    where: { id: thread.id },
    data: {
      lastMessageAt: new Date(),
      isRead: false,
    },
  });

  // Notify team members (fire-and-forget)
  notifyTeamOfInboundMessage({
    teamId: team.id,
    creatorName: creator.name,
    creatorEmail: senderEmail,
    subject,
    body: parsedContent.textBody,
    attachments: [], // Add attachment handling as needed
    threadId: thread.id,
    creatorId: creator.id,
  }).catch(() => {});

  return NextResponse.json({ ok: true, messageId: message.id, direction: "INBOUND" });
}

// ===========================================
// Delivery Status Handler
// ===========================================

async function handleDeliveryStatus(event: ResendWebhookEvent) {
  const eventData = event.data;
  const resendEmailId = eventData.email_id as string | undefined;
  
  if (!resendEmailId) {
    return NextResponse.json({ ok: true });
  }

  const statusMap: Record<string, string> = {
    "email.sent": "SENT",
    "email.delivered": "DELIVERED",
    "email.bounced": "BOUNCED",
  };

  const newStatus = statusMap[event.type];
  if (!newStatus) {
    return NextResponse.json({ ok: true });
  }

  // Update message status
  await prisma.inboxMessage.updateMany({
    where: { resendEmailId },
    data: { deliveryStatus: newStatus as "SENT" | "DELIVERED" | "BOUNCED" },
  });

  return NextResponse.json({ ok: true });
}

// ===========================================
// Helper Functions
// ===========================================

function extractEmail(address: string): string | null {
  const match = address.match(/<([^>]+)>/);
  if (match) return match[1].toLowerCase();
  if (address.includes("@")) return address.toLowerCase().trim();
  return null;
}

function extractName(address: string): string | null {
  const match = address.match(/^([^<]+)</);
  if (match) return match[1].trim();
  return null;
}

/**
 * Check if email is sent to your inbound domain
 */
function hasInboxDomain(addresses: string[]): boolean {
  return addresses.some((addr) => {
    const email = extractEmail(addr);
    return email?.endsWith(`@${DEFAULT_EMAIL_DOMAIN}`);
  });
}

/**
 * Filter out internal inbox addresses, returning only external recipients
 */
function filterExternalRecipients(addresses: string[]): string[] {
  return addresses.filter((addr) => {
    const email = extractEmail(addr);
    return email && !email.endsWith(`@${DEFAULT_EMAIL_DOMAIN}`);
  });
}

/**
 * Find team member by email across all their teams
 */
async function findTeamMemberByEmail(
  email: string,
  teamId: string
): Promise<{ id: string; userId: string } | null> {
  const member = await prisma.teamMember.findFirst({
    where: {
      teamId,
      user: { email: { equals: email, mode: "insensitive" } },
    },
    select: { id: true, userId: true },
  });
  return member;
}

/**
 * Resolve team from recipient email addresses.
 * 
 * Strategy options (customize based on your needs):
 * 1. Single inbound domain: Extract team slug from email prefix (e.g., team-slug@inbox.com)
 * 2. Team-specific subdomains: Extract from domain (e.g., *@team-slug.inbox.com)
 * 3. User mapping: Look up user by email prefix and get their teams
 */
async function resolveTeamFromRecipients(
  toAddresses: string[]
): Promise<{ id: string; slug: string } | null> {
  for (const addr of toAddresses) {
    const email = extractEmail(addr);
    if (!email || !email.endsWith(`@${DEFAULT_EMAIL_DOMAIN}`)) continue;
    
    // Option 1: Extract team slug from email prefix
    // Format: team-slug@inbox.yourdomain.com
    const prefix = email.split("@")[0];
    
    // Look up team by slug
    const team = await prisma.team.findFirst({
      where: { slug: prefix },
      select: { id: true, slug: true },
    });
    if (team) return team;

    // Option 2: Look up user by email prefix and get their default team
    const user = await prisma.user.findFirst({
      where: { 
        email: { startsWith: prefix, mode: "insensitive" } 
      },
      select: {
        teamMemberships: {
          take: 1,
          orderBy: { createdAt: "asc" },
          select: { team: { select: { id: true, slug: true } } },
        },
      },
    });
    if (user?.teamMemberships[0]?.team) {
      return user.teamMemberships[0].team;
    }
  }
  
  return null;
}

/**
 * Enhanced creator resolution with priority:
 * 1. Match sender against Creator.email (primary email)
 * 2. Match sender against CreatorContact.email (associated contacts)
 * 3. Domain matching - find creator whose email domain matches sender
 */
async function resolveCreatorFromEmail(
  senderEmail: string,
  teamId: string
): Promise<{ id: string; name: string | null; email: string | null } | null> {
  // 1. Match against Creator.email (primary email)
  const creator = await prisma.creator.findFirst({
    where: {
      email: { equals: senderEmail, mode: "insensitive" },
      teamId,
    },
    select: { id: true, name: true, email: true },
  });
  if (creator) return creator;

  // 2. Match against CreatorContact.email (if you have this model)
  // Uncomment if you have a CreatorContact model:
  // const contactMatch = await prisma.creatorContact.findFirst({
  //   where: {
  //     email: { equals: senderEmail, mode: "insensitive" },
  //     creator: { teamId },
  //   },
  //   select: { creator: { select: { id: true, name: true, email: true } } },
  // });
  // if (contactMatch?.creator) return contactMatch.creator;

  // 3. Domain matching - find creator with same email domain
  const senderDomain = senderEmail.split("@")[1]?.toLowerCase();
  if (senderDomain) {
    const domainMatch = await prisma.creator.findFirst({
      where: {
        teamId,
        email: { endsWith: `@${senderDomain}`, mode: "insensitive" },
      },
      select: { id: true, name: true, email: true },
    });
    if (domainMatch) return domainMatch;
  }

  return null;
}

async function resolveOrCreateCreator(
  email: string,
  teamId: string,
  name: string | null
): Promise<{ id: string; name: string | null; email: string | null }> {
  // Try enhanced resolution first
  const existing = await resolveCreatorFromEmail(email, teamId);
  if (existing) return existing;

  // Create new creator
  const created = await prisma.creator.create({
    data: {
      teamId,
      email,
      name,
      outreachStatus: "IN_CONVERSATION",
    },
    select: { id: true, name: true, email: true },
  });

  return created;
}
