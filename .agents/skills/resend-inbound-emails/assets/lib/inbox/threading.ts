import { prisma } from "@/lib/prisma";

/**
 * Email Threading Utilities
 * 
 * Implements RFC 5322-based thread matching with fallback to email/creator matching.
 * Uses single-thread-per-creator model: all messages to/from a contact go into one thread.
 */

type InboxThread = Awaited<ReturnType<typeof prisma.inboxThread.findFirst>> & object;

type ThreadWithCreator = InboxThread & {
  creator: { id: string; email: string | null } | null;
};

type HeaderMatchResult = {
  thread: ThreadWithCreator;
  matchedViaHeaders: true;
} | null;

/**
 * Find a thread by RFC 5322 email headers (Message-ID, In-Reply-To, References).
 * Returns the thread WITH its creator info if matched via headers.
 * 
 * Matching priority:
 * 1. Exact Message-ID match (deduplication)
 * 2. In-Reply-To match (direct reply)
 * 3. References match (any message in chain)
 */
export async function findThreadByHeaders({
  teamId,
  messageId,
  inReplyTo,
  references,
}: {
  teamId: string;
  messageId: string | null;
  inReplyTo: string | null;
  references: string[];
}): Promise<HeaderMatchResult> {
  // Check for exact message ID match (deduplication)
  if (messageId) {
    const messageMatch = await prisma.inboxMessage.findFirst({
      where: {
        messageId,
        thread: { teamId },
      },
      select: {
        thread: {
          include: {
            creator: { select: { id: true, email: true } },
          },
        },
      },
    });

    if (messageMatch?.thread) {
      return { thread: messageMatch.thread, matchedViaHeaders: true };
    }
  }

  // Check In-Reply-To header (direct reply)
  if (inReplyTo) {
    const replyMatch = await prisma.inboxMessage.findFirst({
      where: {
        messageId: inReplyTo,
        thread: { teamId },
      },
      select: {
        thread: {
          include: {
            creator: { select: { id: true, email: true } },
          },
        },
      },
    });

    if (replyMatch?.thread) {
      return { thread: replyMatch.thread, matchedViaHeaders: true };
    }
  }

  // Check References header (any message in chain)
  if (references.length > 0) {
    const referenceMatch = await prisma.inboxMessage.findFirst({
      where: {
        messageId: { in: references },
        thread: { teamId },
      },
      orderBy: { createdAt: "desc" },
      select: {
        thread: {
          include: {
            creator: { select: { id: true, email: true } },
          },
        },
      },
    });

    if (referenceMatch?.thread) {
      return { thread: referenceMatch.thread, matchedViaHeaders: true };
    }
  }

  return null;
}

/**
 * Find or create a single thread for a creator.
 * Single-thread-per-creator model: all messages to/from a creator go into one thread.
 * 
 * Priority:
 * 1. Match via RFC 5322 headers (for reply chain continuity)
 * 2. Find existing thread for this creator
 * 3. Create new thread for new creator
 */
export async function findOrCreateCreatorThread({
  teamId,
  creatorId,
  primaryEmail,
  messageId,
  inReplyTo,
  references,
}: {
  teamId: string;
  creatorId: string;
  primaryEmail: string;
  messageId: string | null;
  inReplyTo: string | null;
  references: string[];
}): Promise<NonNullable<InboxThread>> {
  // 1. Try RFC headers first (for reply chain continuity)
  const headerMatch = await findThreadByHeaders({
    teamId,
    messageId,
    inReplyTo,
    references,
  });
  if (headerMatch) {
    return headerMatch.thread;
  }

  // 2. Find existing thread for this creator (single thread model)
  const existingThread = await prisma.inboxThread.findFirst({
    where: { teamId, creatorId },
    orderBy: { createdAt: "asc" }, // Use the original/oldest thread
  });
  if (existingThread) {
    return existingThread;
  }

  // 3. Create new thread for new creator
  return prisma.inboxThread.create({
    data: {
      teamId,
      creatorId,
      creatorEmail: primaryEmail.toLowerCase(),
      primaryEmail: primaryEmail.toLowerCase(),
      isRead: false,
      isArchived: false,
      lastMessageAt: new Date(),
      participantEmails: [primaryEmail.toLowerCase()],
    },
  });
}

/**
 * Add an email to the thread's participant list if not already present.
 */
export async function addThreadParticipant(
  threadId: string,
  email: string
): Promise<void> {
  const normalizedEmail = email.toLowerCase().trim();
  
  const thread = await prisma.inboxThread.findUnique({
    where: { id: threadId },
    select: { participantEmails: true },
  });

  if (!thread) return;

  const participants = thread.participantEmails ?? [];
  if (!participants.includes(normalizedEmail)) {
    await prisma.inboxThread.update({
      where: { id: threadId },
      data: {
        participantEmails: [...participants, normalizedEmail],
      },
    });
  }
}
