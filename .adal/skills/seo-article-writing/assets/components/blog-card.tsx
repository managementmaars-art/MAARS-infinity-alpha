/**
 * Blog Card Components
 * 
 * Copy to: src/components/blog/blog-card.tsx
 * 
 * Displays blog posts in card format for listing pages.
 * Includes both full and compact variants.
 */

import { Link } from "@tanstack/react-router"; // or 'next/link' for Next.js
import { Calendar, Clock, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { BlogPost } from "@/types/blog";

interface BlogCardProps {
  post: BlogPost;
  featured?: boolean;
  className?: string;
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Full blog card with image, title, description, and metadata
 */
export function BlogCard({ post, featured = false, className }: BlogCardProps) {
  return (
    <Link
      to={`/blog/${post.slug}`}
      className={cn(
        "group block rounded-xl border border-border/40 bg-card overflow-hidden",
        "hover:border-border/60 hover:bg-card/80 transition-all duration-200",
        featured && "md:col-span-2",
        className
      )}
    >
      {/* Image */}
      {post.image && (
        <div className="aspect-[2/1] overflow-hidden bg-muted">
          <img
            src={post.image}
            alt={post.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {post.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 text-[10px] font-medium rounded-full bg-primary/10 text-primary"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Title */}
        <h3 className={cn(
          "font-semibold tracking-tight mb-2 group-hover:text-primary transition-colors",
          featured ? "text-lg" : "text-[15px]"
        )}>
          {post.title}
        </h3>

        {/* Description */}
        <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2 mb-3">
          {post.description}
        </p>

        {/* Meta */}
        <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formatDate(post.date)}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {post.readingTime} min read
          </span>
        </div>
      </div>
    </Link>
  );
}

/**
 * Compact blog card for sidebar or related posts
 */
export function BlogCardCompact({ post, className }: BlogCardProps) {
  return (
    <Link
      to={`/blog/${post.slug}`}
      className={cn(
        "group flex items-start gap-3 p-3 rounded-lg",
        "border border-border/40 bg-card/50",
        "hover:border-border/60 hover:bg-card transition-all duration-200",
        className
      )}
    >
      {/* Thumbnail */}
      {post.image && (
        <div className="w-16 h-16 rounded-md overflow-hidden bg-muted shrink-0">
          <img
            src={post.image}
            alt={post.title}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Content */}
      <div className="min-w-0 flex-1">
        <h4 className="text-xs font-semibold line-clamp-2 group-hover:text-primary transition-colors">
          {post.title}
        </h4>
        <div className="flex items-center gap-2 mt-1.5 text-[10px] text-muted-foreground">
          <span>{formatDate(post.date)}</span>
          <span>•</span>
          <span>{post.readingTime} min</span>
        </div>
      </div>

      {/* Arrow */}
      <ArrowRight className="h-3 w-3 text-muted-foreground/50 group-hover:text-primary transition-colors shrink-0 mt-1" />
    </Link>
  );
}

/**
 * Blog card skeleton for loading states
 */
export function BlogCardSkeleton({ featured = false }: { featured?: boolean }) {
  return (
    <div className={cn(
      "rounded-xl border border-border/40 bg-card overflow-hidden",
      featured && "md:col-span-2"
    )}>
      <div className="aspect-[2/1] bg-muted animate-pulse" />
      <div className="p-4 space-y-3">
        <div className="flex gap-1.5">
          <div className="h-4 w-12 rounded-full bg-muted animate-pulse" />
          <div className="h-4 w-16 rounded-full bg-muted animate-pulse" />
        </div>
        <div className="h-5 w-3/4 rounded bg-muted animate-pulse" />
        <div className="space-y-1.5">
          <div className="h-3 w-full rounded bg-muted animate-pulse" />
          <div className="h-3 w-2/3 rounded bg-muted animate-pulse" />
        </div>
        <div className="flex gap-3">
          <div className="h-3 w-20 rounded bg-muted animate-pulse" />
          <div className="h-3 w-16 rounded bg-muted animate-pulse" />
        </div>
      </div>
    </div>
  );
}

export default BlogCard;
