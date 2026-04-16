import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { withErrorHandler, ApiError } from "@/lib/api-helpers";

/**
 * Accept Invitation API Route Template
 * 
 * File: src/app/api/invitations/[token]/accept/route.ts
 * 
 * POST /api/invitations/[token]/accept - Accept a team invitation
 * 
 * The user must be authenticated and the invitation must:
 * - Exist and not be expired
 * - Match the user's email
 * 
 * NOTE: In Next.js 15+, params is a Promise and must be awaited!
 */

type RouteParams = {
  params: Promise<{ token: string }>;
};

export const POST = withErrorHandler(async (_req: NextRequest, { params }: RouteParams) => {
  const session = await auth();
  if (!session?.user?.id || !session?.user?.email) {
    throw new ApiError("Unauthorized", 401);
  }

  // Next.js 15+: params is a Promise
  const { token } = await params;

  // Find the invitation
  const invitation = await prisma.invitation.findUnique({
    where: { token },
    include: {
      team: {
        select: { id: true, name: true, slug: true },
      },
    },
  });

  if (!invitation) {
    throw new ApiError("Invitation not found", 404);
  }

  // Check if expired
  if (invitation.expiresAt < new Date()) {
    // Delete expired invitation
    await prisma.invitation.delete({ where: { id: invitation.id } });
    throw new ApiError("Invitation has expired", 400);
  }

  // Check if email matches
  if (invitation.email.toLowerCase() !== session.user.email.toLowerCase()) {
    throw new ApiError("This invitation was sent to a different email address", 403);
  }

  // Check if already a member
  const existingMember = await prisma.teamMember.findUnique({
    where: {
      userId_teamId: {
        userId: session.user.id,
        teamId: invitation.teamId,
      },
    },
  });

  if (existingMember) {
    // Delete the invitation since they're already a member
    await prisma.invitation.delete({ where: { id: invitation.id } });
    throw new ApiError("You are already a member of this team", 400);
  }

  // Accept invitation: create member and delete invitation in a transaction
  const result = await prisma.$transaction(async (tx) => {
    // Create team member
    const member = await tx.teamMember.create({
      data: {
        userId: session.user.id,
        teamId: invitation.teamId,
        role: invitation.role,
      },
    });

    // Delete the invitation
    await tx.invitation.delete({
      where: { id: invitation.id },
    });

    return member;
  });

  return NextResponse.json({
    success: true,
    team: invitation.team,
    role: result.role,
  });
});
