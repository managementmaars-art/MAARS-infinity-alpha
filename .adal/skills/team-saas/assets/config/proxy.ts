import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Next.js 16 Proxy (formerly middleware)
 * 
 * Authentication is handled in layout.tsx using Server Components.
 * Proxy is only for network-level operations like security headers.
 * 
 * File location: src/proxy.ts
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function proxy(_request: NextRequest): NextResponse {
  const response = NextResponse.next();

  // Security headers
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

  return response;
}

export const config = {
  matcher: [
    // Match all paths except static files
    "/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)",
  ],
};
