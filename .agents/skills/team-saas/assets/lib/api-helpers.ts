import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

/**
 * API Helpers for Team SaaS
 * 
 * Provides consistent error handling, authentication, and request parsing
 * across all API routes.
 */

/**
 * HTTP Error class that includes status code for proper response handling
 */
export class ApiError extends Error {
  constructor(public message: string, public status: number) {
    super(message);
  }
}

/**
 * Get user's role in a team (null if not a member)
 */
export async function getUserTeamRole(userId: string, teamId: string) {
  const member = await prisma.teamMember.findUnique({
    where: { userId_teamId: { userId, teamId } },
  });
  return member?.role ?? null;
}

/**
 * Require authenticated user to be a team member.
 * Returns the user's role or throws 401/403.
 * 
 * Usage:
 *   const { userId, role } = await requireTeamMember(teamId);
 */
export async function requireTeamMember(teamId: string) {
  const session = await auth();

  if (!session?.user?.id) {
    throw new ApiError("Unauthorized", 401);
  }

  const role = await getUserTeamRole(session.user.id, teamId);
  if (!role) {
    throw new ApiError("You are not a member of this team", 403);
  }

  return { userId: session.user.id, role };
}

/**
 * Require admin role in team.
 * Returns user info or throws 401/403.
 */
export async function requireTeamAdmin(teamId: string) {
  const { userId, role } = await requireTeamMember(teamId);
  
  if (role !== "ADMIN") {
    throw new ApiError("Admin access required", 403);
  }
  
  return { userId, role };
}

/**
 * Parse JSON body and validate with Zod schema.
 * Returns validated data or throws 400.
 * 
 * Usage:
 *   const { name, email } = await parseJsonBody(req, mySchema);
 */
export async function parseJsonBody<T>(
  req: NextRequest,
  schema: z.ZodType<T>
): Promise<T> {
  let body;
  try {
    body = await req.json();
  } catch {
    throw new ApiError("Invalid JSON body", 400);
  }

  const validation = schema.safeParse(body);
  if (!validation.success) {
    throw new ApiError(validation.error.issues[0].message, 400);
  }

  return validation.data;
}

/**
 * Wrap handler to catch ApiError and return proper responses.
 * 
 * Usage:
 *   export const GET = withErrorHandler(async (req, { params }) => {
 *     const { teamId } = await params;
 *     // ... your logic
 *     return NextResponse.json(data);
 *   });
 */
export function withErrorHandler<T extends unknown[]>(
  handler: (...args: T) => Promise<NextResponse>
) {
  return async (...args: T): Promise<NextResponse> => {
    try {
      return await handler(...args);
    } catch (error) {
      if (error instanceof ApiError) {
        return NextResponse.json({ error: error.message }, { status: error.status });
      }
      console.error("Unhandled API error:", error);
      return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
  };
}
