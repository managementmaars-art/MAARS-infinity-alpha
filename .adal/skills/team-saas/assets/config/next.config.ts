import type { NextConfig } from "next";

/**
 * Next.js Configuration
 * 
 * Key features:
 * - Image optimization with remote patterns
 * - Rewrites for S3 upload proxy
 */
const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      // Add your allowed image domains here
      // Example:
      // {
      //   protocol: "https",
      //   hostname: "cdn.example.com",
      // },
    ],
  },
  
  async rewrites() {
    return [
      // Proxy uploads from S3 storage through API route
      // This allows serving files from private S3 buckets
      {
        source: "/uploads/:path*",
        destination: "/api/uploads/:path*",
      },
    ];
  },
};

export default nextConfig;
