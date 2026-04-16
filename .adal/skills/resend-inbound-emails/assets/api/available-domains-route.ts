import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

/**
 * Available Domains API
 * 
 * File: src/app/api/users/me/available-domains/route.ts
 * 
 * GET - Get all verified domains from teams the user is a member of
 * Used for the domain selector in user email settings
 */

export interface AvailableDomain {
  domain: string;
  teamId: string;
  teamName: string;
}

export interface AvailableDomainsResponse {
  domains: AvailableDomain[];
}

export async function GET() {
  const session = await auth();

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Get all teams the user is a member of
  const teamMemberships = await prisma.teamMember.findMany({
    where: { userId: session.user.id },
    select: {
      team: {
        select: {
          id: true,
          name: true,
          domains: {
            where: { status: "verified" },
            select: {
              domain: true,
            },
          },
        },
      },
    },
  });

  // Flatten the domains list
  const domains: AvailableDomain[] = [];
  for (const membership of teamMemberships) {
    for (const domainRecord of membership.team.domains) {
      domains.push({
        domain: domainRecord.domain,
        teamId: membership.team.id,
        teamName: membership.team.name,
      });
    }
  }

  return NextResponse.json({ domains } satisfies AvailableDomainsResponse);
}
