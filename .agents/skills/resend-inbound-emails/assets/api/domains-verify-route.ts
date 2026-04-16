import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getResend } from "@/lib/resend";
import { requireTeamAdmin, withErrorHandler, ApiError } from "@/lib/api-helpers";

/**
 * Domain Verification API
 * 
 * File: src/app/api/teams/[teamId]/domains/[domainId]/verify/route.ts
 * 
 * POST - Verify DNS records for a domain
 */

type RouteParams = {
  params: Promise<{ teamId: string; domainId: string }>;
};

export const POST = withErrorHandler(async (_req: NextRequest, { params }: RouteParams) => {
  const { teamId, domainId } = await params;
  await requireTeamAdmin(teamId);

  // Get domain
  const domain = await prisma.teamDomain.findFirst({
    where: { id: domainId, teamId },
  });

  if (!domain) {
    throw new ApiError("Domain not found", 404);
  }

  const resend = getResend();

  // Verify with Resend
  const { error: verifyError } = await resend.domains.verify(domain.resendDomainId);

  if (verifyError) {
    // 502 Bad Gateway for upstream Resend API errors
    throw new ApiError(verifyError.message || "Verification failed", 502);
  }

  // Get updated domain status
  const { data: domainDetails } = await resend.domains.get(domain.resendDomainId);
  const newStatus = domainDetails?.status || domain.status;

  // Update domain status in database
  const updatedDomain = await prisma.teamDomain.update({
    where: { id: domainId },
    data: { status: newStatus },
  });

  return NextResponse.json({
    domain: updatedDomain,
    records: domainDetails?.records || [],
    message: newStatus === "verified"
      ? "Domain verified successfully!"
      : "Verification in progress. DNS records may take time to propagate.",
  });
});
