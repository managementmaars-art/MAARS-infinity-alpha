import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

/**
 * User Profile API
 * 
 * File: src/app/api/users/me/route.ts
 * 
 * GET - Fetch current user profile
 * PATCH - Update user settings (name, theme, notifyInboundEmail, sendFromDomain)
 */

const updateUserSchema = z.object({
  name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(50, "Name must be less than 50 characters")
    .optional(),
  // Image can be a relative path (/uploads/...) or full URL, or null to remove
  image: z.string().optional().nullable(),
  // Theme preference: light, dark, or system
  theme: z.enum(["light", "dark", "system"]).optional(),
  // Notification preferences
  notifyInboundEmail: z.boolean().optional(),
  // Custom sending domain preference (null = use default)
  sendFromDomain: z.string().nullable().optional(),
});

// ===========================================
// GET: Fetch user profile
// ===========================================

export async function GET() {
  const session = await auth();

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: {
      id: true,
      email: true,
      name: true,
      image: true,
      theme: true,
      notifyInboundEmail: true,
      sendFromDomain: true,
      createdAt: true,
    },
  });

  if (!user) {
    return NextResponse.json({ error: "User not found" }, { status: 404 });
  }

  return NextResponse.json(user);
}

// ===========================================
// PATCH: Update user settings
// ===========================================

export async function PATCH(req: NextRequest) {
  const session = await auth();

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const validation = updateUserSchema.safeParse(body);
  if (!validation.success) {
    return NextResponse.json(
      { error: validation.error.issues[0].message },
      { status: 400 }
    );
  }

  const { name, image, theme, notifyInboundEmail, sendFromDomain } = validation.data;

  // Validate sendFromDomain belongs to one of user's teams
  if (sendFromDomain) {
    const validDomain = await prisma.teamDomain.findFirst({
      where: {
        domain: sendFromDomain,
        status: "verified",
        team: {
          members: {
            some: { userId: session.user.id }
          }
        }
      }
    });

    if (!validDomain) {
      return NextResponse.json(
        { error: "Invalid domain. Please select a verified domain from your teams." },
        { status: 400 }
      );
    }
  }

  const user = await prisma.user.update({
    where: { id: session.user.id },
    data: {
      ...(name !== undefined && { name }),
      ...(image !== undefined && { image }),
      ...(theme !== undefined && { theme }),
      ...(notifyInboundEmail !== undefined && { notifyInboundEmail }),
      ...(sendFromDomain !== undefined && { sendFromDomain }),
    },
    select: {
      id: true,
      email: true,
      name: true,
      image: true,
      theme: true,
      notifyInboundEmail: true,
      sendFromDomain: true,
      createdAt: true,
    },
  });

  return NextResponse.json(user);
}
