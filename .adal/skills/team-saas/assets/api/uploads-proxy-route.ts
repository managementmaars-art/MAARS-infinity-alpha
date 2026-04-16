import { NextRequest, NextResponse } from "next/server";
import { getS3Object, getS3ObjectMetadata } from "@/lib/s3";

/**
 * S3 Upload Proxy Route Template
 * 
 * File: src/app/api/uploads/[...path]/route.ts
 * 
 * GET /api/uploads/[...path] - Serve files from S3 with streaming support
 * HEAD /api/uploads/[...path] - Get file metadata
 * 
 * Features:
 * - Range request support for video streaming
 * - Long cache headers for static assets
 * - Streams directly from S3 (no memory buffering)
 * 
 * NOTE: In Next.js 15+, params is a Promise and must be awaited!
 * 
 * Also add this rewrite to next.config.ts:
 *   async rewrites() {
 *     return [
 *       { source: "/uploads/:path*", destination: "/api/uploads/:path*" },
 *     ];
 *   }
 */

type RouteParams = {
  params: Promise<{ path: string[] }>;
};

export async function GET(req: NextRequest, { params }: RouteParams) {
  // Next.js 15+: params is a Promise
  const { path } = await params;
  const key = path.join("/");
  
  if (!key) {
    return NextResponse.json({ error: "Path required" }, { status: 400 });
  }

  // Check for range request (video streaming)
  const range = req.headers.get("range");
  
  if (range) {
    // Partial content request (for video seeking)
    const metadata = await getS3ObjectMetadata(key);
    
    if (!metadata) {
      return NextResponse.json({ error: "File not found" }, { status: 404 });
    }
    
    const result = await getS3Object(key, range);
    
    if (!result) {
      return NextResponse.json({ error: "File not found" }, { status: 404 });
    }

    return new NextResponse(result.body, {
      status: 206, // Partial Content
      headers: {
        "Content-Type": result.contentType,
        "Content-Range": result.contentRange || "",
        "Accept-Ranges": result.acceptRanges,
        "Cache-Control": "public, max-age=31536000, immutable",
      },
    });
  }

  // Regular request - return full file
  const result = await getS3Object(key);
  
  if (!result) {
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  }

  return new NextResponse(result.body, {
    headers: {
      "Content-Type": result.contentType,
      "Content-Length": result.contentLength.toString(),
      "Accept-Ranges": "bytes",
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}

export async function HEAD(_req: NextRequest, { params }: RouteParams) {
  // Next.js 15+: params is a Promise
  const { path } = await params;
  const key = path.join("/");
  
  if (!key) {
    return NextResponse.json({ error: "Path required" }, { status: 400 });
  }

  const metadata = await getS3ObjectMetadata(key);
  
  if (!metadata) {
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  }

  return new NextResponse(null, {
    headers: {
      "Content-Type": metadata.contentType,
      "Content-Length": metadata.contentLength.toString(),
      "Accept-Ranges": "bytes",
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
