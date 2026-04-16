import { randomUUID } from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { 
  buildFromAddress, 
  buildReplyToAddress, 
  getResend, 
  getUserSendingDomain,
  DEFAULT_EMAIL_DOMAIN,
} from "@/lib/resend";
import {
  buildReferencesHeader,
  formatMessageIdHeader,
  mergeReferences,
} from "@/lib/inbox/email-headers";
import { findOrCreateCreatorThread } from "@/lib/inbox/threading";
import { hasLiquidTags } from "@/lib/personalization/process-liquid-tags";

// Email domain for Message-ID generation (use your inbound domain)
const EMAIL_DOMAIN = DEFAULT_EMAIL_DOMAIN;

/**
 * Single Email Send API
 * 
 * File: src/app/api/teams/[teamId]/inbox/send/route.ts
 * 
 * POST - Send a single email with optional personalization
 */

const sendSchema = z.object({
  creatorId: z.string().min(1, "Creator is required"),
  toEmail: z.string().email().optional(),
  subject: z.string().min(1, "Subject is required"),
  text: z.string().min(1, "Text body is required"),
  html: z.string().min(1, "HTML body is required"),
  threadId: z.string().min(1).optional(),
  cc: z.array(z.string().email()).optional(),
  bcc: z.array(z.string().email()).optional(),
});

type RouteParams = {
  params: Promise<{ teamId: string }>;
};

export async function POST(req: NextRequest, { params }: RouteParams) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { teamId } = await params;

  // Verify team membership
  const membership = await prisma.teamMember.findUnique({
    where: { userId_teamId: { userId: session.user.id, teamId } },
  });

  if (!membership) {
    return NextResponse.json({ error: "Not a team member" }, { status: 403 });
  }

  // Parse request body
  let body;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const validation = sendSchema.safeParse(body);
  if (!validation.success) {
    return NextResponse.json(
      { error: validation.error.issues[0].message },
      { status: 400 }
    );
  }

  const { creatorId, toEmail, subject, text, html, threadId, cc, bcc } = validation.data;

  // Get creator and determine recipient
  const creator = await prisma.creator.findFirst({
    where: { id: creatorId, teamId },
    select: { id: true, email: true, name: true },
  });

  if (!creator) {
    return NextResponse.json({ error: "Creator not found" }, { status: 404 });
  }

  const recipientEmail = toEmail || creator.email;
  if (!recipientEmail) {
    return NextResponse.json({ error: "No recipient email" }, { status: 400 });
  }

  // Defense: verify no {{ }} tags remain (should be personalized before sending)
  if (hasLiquidTags(subject) || hasLiquidTags(text)) {
    return NextResponse.json(
      { error: "Email contains unreplaced personalization tags" },
      { status: 422 }
    );
  }

  // Build addresses
  const sendingDomain = await getUserSendingDomain(session.user.id, teamId);
  const fromAddress = buildFromAddress(session.user.email, session.user.name, sendingDomain);
  const replyTo = buildReplyToAddress(session.user.email);
  const messageId = `${randomUUID()}@${DEFAULT_EMAIL_DOMAIN}`;

  // Get or create thread
  let thread;
  let lastMessage: { messageId: string | null; references: string[] } | null = null;

  if (threadId) {
    thread = await prisma.inboxThread.findFirst({
      where: { id: threadId, teamId },
    });
  }

  if (!thread) {
    thread = await findOrCreateCreatorThread({
      teamId,
      creatorId: creator.id,
      primaryEmail: recipientEmail,
      messageId: null,
      inReplyTo: null,
      references: [],
    });
  }

  // Get last message for threading headers
  lastMessage = await prisma.inboxMessage.findFirst({
    where: { threadId: thread.id },
    orderBy: { createdAt: "desc" },
    select: { messageId: true, references: true },
  });

  // Build RFC 5322 threading headers
  const inReplyTo = lastMessage?.messageId ?? null;
  const references = lastMessage
    ? mergeReferences(lastMessage.references ?? [], inReplyTo)
    : [];

  const headers: Record<string, string> = {};
  const messageIdHeader = formatMessageIdHeader(messageId);
  if (messageIdHeader) headers["Message-ID"] = messageIdHeader;
  
  const inReplyToHeader = formatMessageIdHeader(inReplyTo);
  if (inReplyToHeader) headers["In-Reply-To"] = inReplyToHeader;
  
  const referencesHeader = buildReferencesHeader(references);
  if (referencesHeader) headers["References"] = referencesHeader;

  // Send via Resend
  const resend = getResend();
  const { data: emailResult, error: sendError } = await resend.emails.send({
    from: fromAddress,
    to: recipientEmail,
    replyTo,
    subject,
    text,
    html,
    cc,
    bcc,
    headers,
  });

  if (sendError) {
    return NextResponse.json(
      { error: sendError.message || "Failed to send email" },
      { status: 500 }
    );
  }

  // Create inbox message record
  const message = await prisma.inboxMessage.create({
    data: {
      threadId: thread.id,
      direction: "OUTBOUND",
      from: fromAddress,
      to: recipientEmail,
      subject,
      textBody: text,
      htmlBody: html,
      resendEmailId: emailResult?.id,
      messageId,
      inReplyTo,
      references,
      sentAt: new Date(),
      deliveryStatus: "SENT",
    },
  });

  // Update thread
  await prisma.inboxThread.update({
    where: { id: thread.id },
    data: {
      lastMessageAt: new Date(),
      isRead: true,
    },
  });

  return NextResponse.json({
    success: true,
    messageId: message.id,
    resendEmailId: emailResult?.id,
    threadId: thread.id,
  });
}
