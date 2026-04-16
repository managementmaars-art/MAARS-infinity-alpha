/**
 * Blog Post Type Definitions
 * 
 * Copy this file to: src/types/blog.ts
 */

/**
 * Frontmatter metadata for blog posts
 */
export interface BlogMeta {
  /** SEO title (under 60 characters) */
  title: string;
  /** Meta description (150-160 characters) */
  description: string;
  /** Publication date (YYYY-MM-DD) */
  date: string;
  /** Author name */
  author: string;
  /** Category tags for filtering */
  tags: string[];
  /** Optional featured image path */
  image?: string;
  /** Estimated reading time in minutes */
  readingTime: number;
}

/**
 * Full blog post with slug and optional content
 */
export interface BlogPost extends BlogMeta {
  /** URL slug derived from folder name */
  slug: string;
  /** Raw content (if loaded) */
  content?: string;
}

/**
 * Blog post with MDX component for rendering
 */
export interface BlogPostWithComponent extends BlogPost {
  /** MDX component for rendering the post content */
  Component: React.ComponentType;
}

/**
 * Blog listing page props
 */
export interface BlogListingProps {
  posts: BlogPost[];
  tags: string[];
  selectedTag?: string;
}

/**
 * Individual blog post page props
 */
export interface BlogPostPageProps {
  post: BlogPostWithComponent;
  relatedPosts: BlogPost[];
}
