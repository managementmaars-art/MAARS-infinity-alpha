import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getResend } from "@/lib/resend";
import { requireTeamAdmin, withErrorHandler, parseJsonBody, ApiError } from "@/lib/api-helpers";
import { z } from "zod";

/**
 * Team Domain Management API
 * 
 * File: src/app/api/teams/[teamId]/domains/route.ts
 * 
 * GET - List team domains with DNS records
 * POST - Add new domain via Resend API
 */

type RouteParams = {
  params: Promise<{ teamId: string }>;
};

// ===========================================
// GET: List domains
// ===========================================

export const GET = withErrorHandler(async (_req: NextRequest, { params }: RouteParams) => {
  const { teamId } = await params;
  await requireTeamAdmin(teamId);

  const resend = getResend();

  const domains = await prisma.teamDomain.findMany({
    where: { teamId },
    orderBy: { createdAt: "desc" },
  });

  // Fetch DNS records for each domain from Resend
  const domainsWithRecords = await Promise.all(
    domains.map(async (domain) => {
      try {
        const { data } = await resend.domains.get(domain.resendDomainId);
        return {
          ...domain,
          records: data?.records || [],
        };
      } catch {
        return { ...domain, records: [] };
      }
    })
  );

  return NextResponse.json(domainsWithRecords);
});

// ===========================================
// POST: Add domain
// ===========================================

const addDomainSchema = z.object({
  domain: z.string().min(1).transform((d) => d.toLowerCase().trim()),
});

export const POST = withErrorHandler(async (req: NextRequest, { params }: RouteParams) => {
  const { teamId } = await params;
  await requireTeamAdmin(teamId);

  const { domain: normalizedDomain } = await parseJsonBody(req, addDomainSchema);

  // Check if domain already exists for this team
  const existing = await prisma.teamDomain.findUnique({
    where: { teamId_domain: { teamId, domain: normalizedDomain } },
  });

  if (existing) {
    throw new ApiError("Domain already added to this team", 400);
  }

  const resend = getResend();

  // Create domain in Resend
  const { data: resendDomain, error: resendError } = await resend.domains.create({
    name: normalizedDomain,
  });

  if (resendError) {
    // Handle "already registered" case - domain might be registered by same account
    if (resendError.message?.toLowerCase().includes("already")) {
      // Try to find existing domain in Resend
      const { data: domainsData } = await resend.domains.list();
      const existingResendDomain = domainsData?.data?.find(
        (d: { name: string }) => d.name.toLowerCase() === normalizedDomain
      );

      if (existingResendDomain) {
        // Check if this Resend domain is already used by another team
        const existingTeamDomain = await prisma.teamDomain.findUnique({
          where: { resendDomainId: existingResendDomain.id },
        });
        
        if (existingTeamDomain && existingTeamDomain.teamId !== teamId) {
          throw new ApiError("Domain already registered in another Resend account", 400);
        }

        // Use existing Resend domain
        const teamDomain = await prisma.teamDomain.create({
          data: {
            teamId,
            resendDomainId: existingResendDomain.id,
            domain: normalizedDomain,
            status: existingResendDomain.status || "not_started",
            isActive: false,
          },
        });

        const { data: domainDetails } = await resend.domains.get(existingResendDomain.id);

        return NextResponse.json({
          domain: teamDomain,
          records: domainDetails?.records || [],
        });
      }
    }

    // 502 Bad Gateway for upstream Resend API errors
    throw new ApiError(resendError.message || "Failed to create domain", 502);
  }

  if (!resendDomain) {
    throw new ApiError("Failed to create domain", 500);
  }

  // Create TeamDomain record
  const teamDomain = await prisma.teamDomain.create({
    data: {
      teamId,
      resendDomainId: resendDomain.id,
      domain: normalizedDomain,
      status: resendDomain.status || "not_started",
      isActive: false,
    },
  });

  // Fetch full domain details including DNS records
  const { data: domainDetails } = await resend.domains.get(resendDomain.id);

  return NextResponse.json({
    domain: teamDomain,
    records: domainDetails?.records || [],
  });
});
