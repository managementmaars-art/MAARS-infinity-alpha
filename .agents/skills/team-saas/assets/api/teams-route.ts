import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { withErrorHandler, parseJsonBody, ApiError } from "@/lib/api-helpers";
import { z } from "zod";

/**
 * Teams API Route Template
 * 
 * File: src/app/api/teams/route.ts
 * 
 * GET /api/teams - List all teams for the current user
 * POST /api/teams - Create a new team (user becomes ADMIN)
 */

// ===========================================
// GET: List user's teams
// ===========================================

export const GET = withErrorHandler(async () => {
  const session = await auth();
  if (!session?.user?.id) {
    throw new ApiError("Unauthorized", 401);
  }

  const teams = await prisma.team.findMany({
    where: {
      members: {
        some: { userId: session.user.id },
      },
    },
    include: {
      members: {
        where: { userId: session.user.id },
        select: { role: true },
      },
      _count: {
        select: { members: true },
      },
    },
    orderBy: { createdAt: "desc" },
  });

  // Format response
  const formattedTeams = teams.map((team) => ({
    id: team.id,
    name: team.name,
    slug: team.slug,
    logo: team.logo,
    role: team.members[0]?.role ?? "MEMBER",
    memberCount: team._count.members,
    createdAt: team.createdAt,
  }));

  return NextResponse.json(formattedTeams);
});

// ===========================================
// POST: Create new team
// ===========================================

const createTeamSchema = z.object({
  name: z.string().min(2).max(50),
  logo: z.string().url().optional(),
});

export const POST = withErrorHandler(async (req: NextRequest) => {
  const session = await auth();
  if (!session?.user?.id) {
    throw new ApiError("Unauthorized", 401);
  }

  const { name, logo } = await parseJsonBody(req, createTeamSchema);

  // Generate unique slug from name
  const baseSlug = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  
  let slug = baseSlug;
  let counter = 1;
  
  // Ensure slug is unique
  while (await prisma.team.findUnique({ where: { slug } })) {
    slug = `${baseSlug}-${counter}`;
    counter++;
  }

  // Create team with user as ADMIN
  const team = await prisma.team.create({
    data: {
      name,
      slug,
      logo,
      members: {
        create: {
          userId: session.user.id,
          role: "ADMIN",
        },
      },
    },
    include: {
      members: {
        where: { userId: session.user.id },
        select: { role: true },
      },
    },
  });

  return NextResponse.json({
    id: team.id,
    name: team.name,
    slug: team.slug,
    logo: team.logo,
    role: team.members[0]?.role ?? "ADMIN",
    createdAt: team.createdAt,
  });
});
