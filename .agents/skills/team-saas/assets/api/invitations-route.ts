import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { sendInvitationEmail } from "@/lib/resend";
import { withErrorHandler, requireTeamAdmin, parseJsonBody, ApiError } from "@/lib/api-helpers";
import { z } from "zod";

/**
 * Team Invitations API Route Template
 * 
 * File: src/app/api/teams/[teamId]/invitations/route.ts
 * 
 * GET /api/teams/[teamId]/invitations - List pending invitations (ADMIN only)
 * POST /api/teams/[teamId]/invitations - Send a new invitation (ADMIN only)
 * 
 * NOTE: In Next.js 15+, params is a Promise and must be awaited!
 */

type RouteParams = {
  params: Promise<{ teamId: string }>;
};

// ===========================================
// GET: List pending invitations
// ===========================================

export const GET = withErrorHandler(async (_req: NextRequest, { params }: RouteParams) => {
  // Next.js 15+: params is a Promise
  const { teamId } = await params;
  
  // Require admin access
  await requireTeamAdmin(teamId);

  const invitations = await prisma.invitation.findMany({
    where: { teamId },
    include: {
      inviter: {
        select: { name: true, email: true },
      },
    },
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(invitations);
});

// ===========================================
// POST: Send new invitation
// ===========================================

const inviteSchema = z.object({
  email: z.string().email(),
  role: z.enum(["ADMIN", "MEMBER"]).optional().default("MEMBER"),
});

export const POST = withErrorHandler(async (req: NextRequest, { params }: RouteParams) => {
  // Next.js 15+: params is a Promise
  const { teamId } = await params;
  
  // Require admin access and get user info
  const { userId } = await requireTeamAdmin(teamId);
  
  // Parse and validate body
  const { email, role } = await parseJsonBody(req, inviteSchema);

  // Check if user is already a member
  const existingUser = await prisma.user.findUnique({
    where: { email },
    include: {
      teamMembers: {
        where: { teamId },
      },
    },
  });

  if (existingUser?.teamMembers.length) {
    throw new ApiError("User is already a team member", 400);
  }

  // Check for existing pending invitation
  const existingInvitation = await prisma.invitation.findUnique({
    where: { email_teamId: { email, teamId } },
  });

  if (existingInvitation) {
    throw new ApiError("Invitation already sent to this email", 400);
  }

  // Get team details for the email
  const team = await prisma.team.findUnique({
    where: { id: teamId },
  });

  if (!team) {
    throw new ApiError("Team not found", 404);
  }

  // Get inviter details
  const inviter = await prisma.user.findUnique({
    where: { id: userId },
    select: { name: true, email: true },
  });

  // Create invitation (expires in 7 days)
  const invitation = await prisma.invitation.create({
    data: {
      email,
      role,
      teamId,
      invitedBy: userId,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    },
  });

  // Send invitation email
  const inviteUrl = `${process.env.NEXT_PUBLIC_APP_URL}/invite/${invitation.token}`;
  
  await sendInvitationEmail({
    to: email,
    inviterName: inviter?.name || inviter?.email || "A team member",
    teamName: team.name,
    inviteUrl,
  });

  return NextResponse.json(invitation);
});
