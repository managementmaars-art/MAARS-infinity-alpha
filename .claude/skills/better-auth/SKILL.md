---
name: better-auth
description: better-auth library for full-stack TypeScript authentication with providers, email/password, organizations, 2FA, and database adapters.
---

# better-auth

## Overview

better-auth is a TypeScript-first authentication library that handles sessions, OAuth providers, email/password, organizations, 2FA, and more. It works with any framework and supports multiple database adapters.

## Installation & Core Setup

```bash
npm install better-auth
# Database adapters
npm install @better-auth/prisma-adapter   # Prisma
npm install @better-auth/drizzle-adapter  # Drizzle
# Optional plugins
npm install @better-auth/organization @better-auth/two-factor
```

```typescript
// lib/auth.ts - Server-side auth instance
import { betterAuth } from "better-auth";
import { prismaAdapter } from "@better-auth/prisma-adapter";
import { organization } from "@better-auth/organization";
import { twoFactor } from "@better-auth/two-factor";
import { emailOTP } from "@better-auth/email-otp";
import { prisma } from "./prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),

  // Email & Password auth
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
    requireEmailVerification: true,
    sendResetPasswordToken: async ({ user, token }) => {
      await sendEmail({
        to: user.email,
        subject: "Reset your password",
        html: `<a href="${process.env.APP_URL}/reset-password?token=${token}">Reset password</a>`,
      });
    },
  },

  // Email verification
  emailVerification: {
    sendVerificationEmail: async ({ user, token }) => {
      await sendEmail({
        to: user.email,
        subject: "Verify your email",
        html: `<a href="${process.env.APP_URL}/verify-email?token=${token}">Verify email</a>`,
      });
    },
    autoSignInAfterVerification: true,
  },

  // OAuth Providers
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    discord: {
      clientId: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
    },
  },

  // Plugins
  plugins: [
    organization({
      allowUserToCreateOrganization: true,
      organizationLimit: 5,
      membershipLimit: 100,
      invitationExpiresIn: 48 * 60 * 60, // 48 hours
      sendInvitationEmail: async ({ invitation, inviter, organization }) => {
        await sendEmail({
          to: invitation.email,
          subject: `Join ${organization.name} on our platform`,
          html: `<a href="${process.env.APP_URL}/accept-invitation?token=${invitation.id}">Accept invitation</a>`,
        });
      },
    }),
    twoFactor({
      issuer: "MyApp",
      otpOptions: {
        period: 30,
        digits: 6,
      },
    }),
    emailOTP({
      sendVerificationOTP: async ({ email, otp, type }) => {
        await sendEmail({
          to: email,
          subject: `Your OTP code: ${otp}`,
          html: `<p>Your ${type} code is: <strong>${otp}</strong></p><p>Expires in 10 minutes.</p>`,
        });
      },
      expiresIn: 600, // 10 minutes
    }),
  ],

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 30,     // 30 days
    updateAge: 60 * 60 * 24,            // Refresh if 1 day old
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,                   // Cache session for 5 minutes
    },
  },

  // Rate limiting
  rateLimit: {
    enabled: true,
    window: 60,
    max: 10,
    storage: "database",               // or "memory"
  },

  // Trusted origins for CSRF protection
  trustedOrigins: [process.env.APP_URL!, "https://app.example.com"],

  // User model customization
  user: {
    additionalFields: {
      role: {
        type: "string",
        defaultValue: "user",
        input: false,                  // Not settable by user
      },
      plan: {
        type: "string",
        defaultValue: "free",
      },
    },
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
```

## Route Handler (Next.js App Router)

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

```typescript
// For other frameworks (Express, Hono, etc.)
import { toNodeHandler } from "better-auth/node";
app.all("/api/auth/*", toNodeHandler(auth));

// Hono
import { toHonoHandler } from "better-auth/hono";
app.all("/api/auth/*", toHonoHandler(auth));
```

## Client Setup

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/react";
import { organizationClient } from "@better-auth/organization/client";
import { twoFactorClient } from "@better-auth/two-factor/client";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [
    organizationClient(),
    twoFactorClient({
      onTwoFactorRedirect: () => {
        window.location.href = "/two-factor";
      },
    }),
  ],
});

// Destructure for convenient imports
export const {
  signIn,
  signOut,
  signUp,
  useSession,
  organization,
  twoFactor,
} = authClient;
```

## React Components

```tsx
// components/auth/SignInForm.tsx
"use client";
import { signIn } from "@/lib/auth-client";
import { useState } from "react";

export function SignInForm() {
  const [error, setError] = useState("");

  const handleEmailSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const { error } = await signIn.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
      callbackURL: "/dashboard",
      rememberMe: true,
    });

    if (error) setError(error.message);
  };

  const handleGoogleSignIn = () => {
    signIn.social({ provider: "google", callbackURL: "/dashboard" });
  };

  return (
    <form onSubmit={handleEmailSignIn}>
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      {error && <p>{error}</p>}
      <button type="submit">Sign In</button>
      <button type="button" onClick={handleGoogleSignIn}>
        Sign in with Google
      </button>
    </form>
  );
}

// Hook for session data
function Dashboard() {
  const { data: session, isPending, error } = useSession();

  if (isPending) return <Spinner />;
  if (!session) return <Redirect to="/login" />;

  return <div>Welcome, {session.user.name}</div>;
}
```

## Organization Management

```typescript
// Organization CRUD operations
const { organization } = authClient;

// Create organization
const org = await organization.create({
  name: "Acme Corp",
  slug: "acme-corp",
  logo: "https://example.com/logo.png",
  metadata: { plan: "enterprise" },
});

// Invite member
await organization.inviteMember({
  email: "colleague@example.com",
  role: "member",         // "owner" | "admin" | "member"
  organizationId: org.id,
});

// Switch active organization
await organization.setActive({ organizationId: org.id });

// Get current organization
const { data: activeOrg } = await organization.getFullOrganization();

// Server-side: check organization membership
import { auth } from "@/lib/auth";

async function requireOrgAdmin(request: Request, orgId: string) {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session) throw new Error("Unauthorized");

  const member = await auth.api.getOrganizationMember({
    organizationId: orgId,
    userId: session.user.id,
  });

  if (!["owner", "admin"].includes(member?.role)) {
    throw new Error("Forbidden");
  }

  return session;
}
```

## Two-Factor Authentication

```typescript
// Enable 2FA for a user
const { totpURI, backupCodes } = await twoFactor.enable({
  password: currentPassword,
});

// Show QR code to user
import QRCode from "qrcode";
const qrDataURL = await QRCode.toDataURL(totpURI);

// Verify and confirm 2FA setup
await twoFactor.verifyTotp({ code: "123456" });

// Sign in with 2FA
await signIn.email({ email, password });
// If 2FA is required, the user is redirected to /two-factor
// Then verify:
await twoFactor.verifyTotp({ code: userInput });

// Disable 2FA
await twoFactor.disable({ password: currentPassword });
```

## Prisma Schema

```prisma
// prisma/schema.prisma
model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified Boolean   @default(false)
  image         String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
  role          String    @default("user")
  plan          String    @default("free")

  sessions      Session[]
  accounts      Account[]
  members       Member[]
  twoFactors    TwoFactor[]
}

model Session {
  id        String   @id @default(cuid())
  expiresAt DateTime
  token     String   @unique
  ipAddress String?
  userAgent String?
  userId    String
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Account {
  id                    String  @id @default(cuid())
  accountId             String
  providerId            String
  userId                String
  user                  User    @relation(fields: [userId], references: [id], onDelete: Cascade)
  accessToken           String?
  refreshToken          String?
  accessTokenExpiresAt  DateTime?
  refreshTokenExpiresAt DateTime?
  scope                 String?
  idToken               String?
  createdAt             DateTime @default(now())
  updatedAt             DateTime @updatedAt

  @@unique([providerId, accountId])
}

model Verification {
  id         String    @id @default(cuid())
  identifier String
  value      String
  expiresAt  DateTime
  createdAt  DateTime? @default(now())
  updatedAt  DateTime? @updatedAt

  @@unique([identifier, value])
}

// Organization plugin tables
model Organization {
  id        String   @id @default(cuid())
  name      String
  slug      String   @unique
  logo      String?
  metadata  String?
  createdAt DateTime @default(now())
  members   Member[]
  invitations Invitation[]
}

model Member {
  id             String       @id @default(cuid())
  organizationId String
  userId         String
  role           String
  createdAt      DateTime     @default(now())
  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  user           User         @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([organizationId, userId])
}
```

## Key Patterns

- **`auth.$Infer.Session`** gives you TypeScript types for session and user
- **Plugin system** is composable — add only what you need
- **`cookieCache`** reduces database reads on every request
- **`trustedOrigins`** must include all your app URLs to prevent CSRF
- **Rate limiting** should use `"database"` storage in production (not in-memory)
- **Organization plugin** handles multi-tenancy with built-in role management

## Models to Use

- **claude-opus-4-5**: Multi-tenant auth architecture, custom plugin development
- **claude-sonnet-4-5**: Provider setup, organization flows, 2FA implementation
- **claude-haiku-3-5**: Simple sign-in/sign-out components, session checks
