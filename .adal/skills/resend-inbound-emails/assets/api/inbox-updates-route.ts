import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { getUserTeamRole } from "@/lib/api-helpers";

/**
 * Inbox Updates API
 * 
 * File: src/app/api/teams/[teamId]/inbox/updates/route.ts
 * 
 * GET - Fetch new inbound messages since a timestamp
 * Used by the polling hook for toast notifications
 */

type RouteParams = {
  params: Promise<{ teamId: string }>;
};

export async function GET(req: NextRequest, { params }: RouteParams) {
  const session = await auth();

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { teamId } = await params;

  const userRole = await getUserTeamRole(session.user.id, teamId);
  if (!userRole) {
    return NextResponse.json(
      { error: "You are not a member of this team" },
      { status: 403 }
    );
  }

  // Get last check timestamp from query or default to 15 seconds ago
  const { searchParams } = new URL(req.url);
  const sinceParam = searchParams.get("since");
  const since = sinceParam
    ? new Date(sinceParam)
    : new Date(Date.now() - 15000);

  // Find new inbound messages since the given timestamp
  const newMessages = await prisma.inboxMessage.findMany({
    where: {
      thread: { teamId },
      direction: "INBOUND",
      receivedAt: { gt: since },
    },
    include: {
      thread: {
        include: {
          creator: {
            select: { id: true, name: true, email: true },
          },
        },
      },
    },
    orderBy: { receivedAt: "desc" },
    take: 10, // Limit to prevent overwhelming the client
  });

  return NextResponse.json({
    newMessages: newMessages.map((m) => ({
      id: m.id,
      creatorId: m.thread.creatorId,
      creatorName: m.thread.creator?.name ?? m.thread.creator?.email ?? "Unknown",
      subject: m.subject,
      preview: (m.textBody ?? "").slice(0, 80),
      receivedAt: m.receivedAt?.toISOString() ?? m.createdAt.toISOString(),
    })),
    timestamp: new Date().toISOString(),
  });
}
