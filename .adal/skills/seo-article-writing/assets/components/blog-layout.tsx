/**
 * Blog Post Layout Component
 * 
 * Copy to: src/components/blog/blog-layout.tsx
 * 
 * Wraps individual blog posts with:
 * - Header with title, meta, and featured image
 * - Prose styling for MDX content
 * - Related posts section
 * - Back to blog navigation
 */

import { Link } from "@tanstack/react-router"; // or 'next/link' for Next.js
import { Calendar, Clock, ArrowLeft, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { BlogPost, BlogPostWithComponent } from "@/types/blog";
import { BlogCardCompact } from "./blog-card";

interface BlogLayoutProps {
  post: BlogPostWithComponent;
  relatedPosts?: BlogPost[];
  children?: React.ReactNode;
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Blog post layout with header, content, and footer
 */
export function BlogLayout({ post, relatedPosts = [], children }: BlogLayoutProps) {
  const { Component } = post;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40">
        <div className="container px-4 mx-auto max-w-3xl py-4">
          <Link to="/blog">
            <Button variant="ghost" size="sm" className="h-8 px-2 text-xs -ml-2">
              <ArrowLeft className="h-3 w-3 mr-1" />
              Back to Blog
            </Button>
          </Link>
        </div>
      </header>

      {/* Featured Image */}
      {post.image && (
        <div className="w-full aspect-[3/1] max-h-[300px] overflow-hidden bg-muted">
          <img
            src={post.image}
            alt={post.title}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Article */}
      <article className="container px-4 mx-auto max-w-3xl py-8 md:py-12">
        {/* Post Header */}
        <header className="mb-8">
          {/* Tags */}
          <div className="flex flex-wrap gap-1.5 mb-4">
            {post.tags.map((tag) => (
              <Link
                key={tag}
                to={`/blog?tag=${tag}`}
                className="px-2.5 py-1 text-[11px] font-medium rounded-full bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
              >
                {tag}
              </Link>
            ))}
          </div>

          {/* Title */}
          <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold tracking-tight mb-4">
            {post.title}
          </h1>

          {/* Description */}
          <p className="text-muted-foreground text-sm md:text-base leading-relaxed mb-6">
            {post.description}
          </p>

          {/* Meta */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground pb-6 border-b border-border/40">
            <span className="flex items-center gap-1.5">
              <User className="h-3.5 w-3.5" />
              {post.author}
            </span>
            <span className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              {formatDate(post.date)}
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              {post.readingTime} min read
            </span>
          </div>
        </header>

        {/* Content */}
        <div className={cn(
          "prose prose-sm md:prose-base max-w-none",
          "dark:prose-invert",
          // Headings
          "prose-headings:font-semibold prose-headings:tracking-tight",
          "prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-4",
          "prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3",
          // Paragraphs
          "prose-p:text-muted-foreground prose-p:leading-relaxed",
          // Links
          "prose-a:text-primary prose-a:no-underline hover:prose-a:underline",
          // Lists
          "prose-li:text-muted-foreground",
          // Code
          "prose-code:text-xs prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:rounded",
          "prose-pre:bg-muted prose-pre:border prose-pre:border-border/40",
          // Tables
          "prose-table:text-sm",
          "prose-th:text-left prose-th:font-semibold prose-th:text-foreground",
          "prose-td:text-muted-foreground",
          // Blockquotes
          "prose-blockquote:border-l-primary prose-blockquote:bg-muted/30 prose-blockquote:py-1 prose-blockquote:not-italic",
          // Images
          "prose-img:rounded-lg prose-img:border prose-img:border-border/40"
        )}>
          {children || <Component />}
        </div>

        {/* Article Footer */}
        <footer className="mt-12 pt-8 border-t border-border/40">
          {/* CTA */}
          <div className="bg-muted/30 rounded-xl p-6 text-center mb-8">
            <h3 className="text-lg font-semibold mb-2">Ready to get started?</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Try Open Sunsama free and see how time blocking can transform your productivity.
            </p>
            <Button size="sm" asChild>
              <Link to="/register">Create Free Account</Link>
            </Button>
          </div>

          {/* Related Posts */}
          {relatedPosts.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold mb-4">Related Articles</h3>
              <div className="grid gap-3">
                {relatedPosts.map((relatedPost) => (
                  <BlogCardCompact key={relatedPost.slug} post={relatedPost} />
                ))}
              </div>
            </div>
          )}
        </footer>
      </article>

      {/* Page Footer */}
      <footer className="border-t border-border/40 py-6">
        <div className="container px-4 mx-auto max-w-3xl">
          <div className="flex justify-between items-center text-xs text-muted-foreground">
            <Link to="/" className="hover:text-foreground transition-colors">
              © 2026 Open Sunsama
            </Link>
            <div className="flex gap-4">
              <Link to="/blog" className="hover:text-foreground transition-colors">
                Blog
              </Link>
              <Link to="/privacy" className="hover:text-foreground transition-colors">
                Privacy
              </Link>
              <Link to="/terms" className="hover:text-foreground transition-colors">
                Terms
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default BlogLayout;
