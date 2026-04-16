import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { requireTeamAdmin, withErrorHandler, ApiError } from "@/lib/api-helpers";

/**
 * Domain Activation API
 * 
 * File: src/app/api/teams/[teamId]/domains/[domainId]/activate/route.ts
 * 
 * PUT - Activate domain (deactivates all others)
 * DELETE - Deactivate domain
 */

type RouteParams = {
  params: Promise<{ teamId: string; domainId: string }>;
};

// ===========================================
// PUT: Activate domain
// ===========================================

export const PUT = withErrorHandler(async (_req: NextRequest, { params }: RouteParams) => {
  const { teamId, domainId } = await params;
  await requireTeamAdmin(teamId);

  // Get domain and verify it's verified
  const domain = await prisma.teamDomain.findFirst({
    where: { id: domainId, teamId },
  });

  if (!domain) {
    throw new ApiError("Domain not found", 404);
  }

  if (domain.status !== "verified") {
    throw new ApiError("Domain must be verified before activation", 400);
  }

  // Deactivate all other domains and activate this one
  await prisma.$transaction([
    // Deactivate all team domains
    prisma.teamDomain.updateMany({
      where: { teamId },
      data: { isActive: false },
    }),
    // Activate the target domain
    prisma.teamDomain.update({
      where: { id: domainId },
      data: { isActive: true },
    }),
  ]);

  const updatedDomain = await prisma.teamDomain.findUnique({
    where: { id: domainId },
  });

  return NextResponse.json({ domain: updatedDomain });
});

// ===========================================
// DELETE: Deactivate domain
// ===========================================

export const DELETE = withErrorHandler(async (_req: NextRequest, { params }: RouteParams) => {
  const { teamId, domainId } = await params;
  await requireTeamAdmin(teamId);

  const domain = await prisma.teamDomain.findFirst({
    where: { id: domainId, teamId },
  });

  if (!domain) {
    throw new ApiError("Domain not found", 404);
  }

  const updatedDomain = await prisma.teamDomain.update({
    where: { id: domainId },
    data: { isActive: false },
  });

  return NextResponse.json({ domain: updatedDomain });
});
