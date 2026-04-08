---
name: vercel-nextjs
description: Next.js App Router, Server Components, Server Actions, Vercel deployment, edge middleware, ISR, streaming for MAARS frontend agents
---

# Vercel / Next.js — MAARS Reference

## App Router Fundamentals
```typescript
// app/page.tsx — Server Component (default)
export default async function HomePage() {
  const data = await fetch("https://api.example.com/data", {
    next: { revalidate: 60 },  // ISR: revalidate every 60s
  });
  const items = await data.json();
  return <ItemList items={items} />;
}

// app/users/[id]/page.tsx — Dynamic route
export async function generateStaticParams() {
  const users = await getUsers();
  return users.map(u => ({ id: u.id.toString() }));
}

export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await getUser(parseInt(params.id));
  if (!user) notFound();
  return <UserProfile user={user} />;
}

// Metadata
export async function generateMetadata({ params }) {
  const user = await getUser(params.id);
  return { title: user.name, description: user.bio };
}
```

## Server Actions
```typescript
// app/actions.ts
"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { redirect } from "next/navigation";

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string;
  const content = formData.get("content") as string;
  
  // Validate
  if (!title || title.length < 3) {
    return { error: "Title too short" };
  }
  
  // DB operation
  const post = await db.posts.create({ data: { title, content } });
  
  // Revalidate cache
  revalidatePath("/blog");
  revalidateTag("posts");
  
  // Redirect
  redirect(`/blog/${post.id}`);
}

// In component:
// <form action={createPost}>
// Or: const [state, formAction] = useFormState(createPost, initialState);
```

## Streaming & Suspense
```typescript
import { Suspense } from "react";

// app/dashboard/page.tsx
export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />  {/* Streams independently */}
      </Suspense>
      <Suspense fallback={<FeedSkeleton />}>
        <ActivityFeed />  {/* Streams independently */}
      </Suspense>
    </div>
  );
}

// Streaming with loading.tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <DashboardSkeleton />;
}
```

## Route Handlers (API)
```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") ?? "1");
  
  const users = await db.users.findMany({ skip: (page-1)*20, take: 20 });
  return NextResponse.json({ users, page });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await db.users.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}

// app/api/users/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await db.users.findUnique({ where: { id: parseInt(params.id) } });
  if (!user) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(user);
}
```

## Middleware
```typescript
// middleware.ts (runs on every request at edge)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Auth check
  const token = request.cookies.get("auth-token");
  if (pathname.startsWith("/dashboard") && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  
  // Add headers
  const response = NextResponse.next();
  response.headers.set("x-request-id", crypto.randomUUID());
  
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

## Client Components
```typescript
"use client";

import { useState, useTransition, useOptimistic } from "react";

export function LikeButton({ postId, initialLikes }: Props) {
  const [isPending, startTransition] = useTransition();
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    initialLikes,
    (state, increment: number) => state + increment
  );
  
  async function handleLike() {
    addOptimisticLike(1);  // Immediate UI update
    startTransition(async () => {
      await likePost(postId);  // Server Action
    });
  }
  
  return (
    <button onClick={handleLike} disabled={isPending}>
      ❤️ {optimisticLikes}
    </button>
  );
}
```

## Caching Strategies
```typescript
// Fetch cache options
fetch(url, { cache: "force-cache" });        // Static (default)
fetch(url, { cache: "no-store" });           // Dynamic, never cache
fetch(url, { next: { revalidate: 60 } });    // ISR every 60s
fetch(url, { next: { tags: ["posts"] } });   // Tag-based revalidation

// On-demand revalidation
import { revalidateTag, revalidatePath } from "next/cache";
await revalidateTag("posts");
await revalidatePath("/blog");

// unstable_cache for non-fetch data
import { unstable_cache } from "next/cache";
const getCachedUser = unstable_cache(
  async (id: string) => db.users.findUnique({ where: { id } }),
  ["user"],
  { revalidate: 3600, tags: ["users"] }
);
```

## next.config.ts
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**.amazonaws.com" }],
  },
  experimental: {
    ppr: true,           // Partial Prerendering
    serverActions: { allowedOrigins: ["example.com"] },
  },
  async redirects() {
    return [{ source: "/old", destination: "/new", permanent: true }];
  },
};

export default nextConfig;
```

## Models to Use
- **Next.js architecture**: `claude-sonnet-4-6` (knows App Router well)
- **Server Actions / complex data flow**: `claude-opus-4-6`
- **Performance optimization**: `claude-sonnet-4-6`
