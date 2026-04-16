/**
 * Blog Utility Functions
 * 
 * Copy this file to: src/lib/blog.ts
 * 
 * Works with Vite's import.meta.glob for MDX loading
 */

import type { BlogPost, BlogPostWithComponent, BlogMeta } from '@/types/blog';

/**
 * Load all blog posts using Vite's glob import
 * MDX files must export frontmatter as a named export
 */
const modules = import.meta.glob<{
  frontmatter: BlogMeta;
  default: React.ComponentType;
}>('../content/blog/*/index.mdx', { eager: true });

/**
 * Extract slug from file path
 * '../content/blog/my-article/index.mdx' -> 'my-article'
 */
function getSlugFromPath(path: string): string {
  const match = path.match(/\/blog\/([^/]+)\/index\.mdx$/);
  return match ? match[1] : '';
}

/**
 * Get all blog posts sorted by date (newest first)
 */
export function getAllBlogPosts(): BlogPost[] {
  const posts: BlogPost[] = [];

  for (const [path, module] of Object.entries(modules)) {
    const slug = getSlugFromPath(path);
    
    if (slug && module.frontmatter) {
      posts.push({
        ...module.frontmatter,
        slug,
      });
    }
  }

  // Sort by date descending
  return posts.sort((a, b) => 
    new Date(b.date).getTime() - new Date(a.date).getTime()
  );
}

/**
 * Get a single blog post by slug with its MDX component
 */
export function getBlogPost(slug: string): BlogPostWithComponent | null {
  for (const [path, module] of Object.entries(modules)) {
    const postSlug = getSlugFromPath(path);
    
    if (postSlug === slug && module.frontmatter) {
      return {
        ...module.frontmatter,
        slug: postSlug,
        Component: module.default,
      };
    }
  }

  return null;
}

/**
 * Get blog posts filtered by tag
 */
export function getBlogPostsByTag(tag: string): BlogPost[] {
  return getAllBlogPosts().filter(post => 
    post.tags.some(t => t.toLowerCase() === tag.toLowerCase())
  );
}

/**
 * Get all unique tags from all posts
 */
export function getAllTags(): string[] {
  const tags = new Set<string>();
  
  for (const post of getAllBlogPosts()) {
    for (const tag of post.tags) {
      tags.add(tag);
    }
  }

  return Array.from(tags).sort();
}

/**
 * Get related posts based on shared tags
 */
export function getRelatedPosts(currentSlug: string, limit = 3): BlogPost[] {
  const currentPost = getAllBlogPosts().find(p => p.slug === currentSlug);
  
  if (!currentPost) return [];

  const otherPosts = getAllBlogPosts().filter(p => p.slug !== currentSlug);
  
  // Score posts by number of shared tags
  const scored = otherPosts.map(post => ({
    post,
    score: post.tags.filter(tag => 
      currentPost.tags.includes(tag)
    ).length,
  }));

  // Sort by score and return top N
  return scored
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(s => s.post);
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Generate reading time text
 */
export function formatReadingTime(minutes: number): string {
  return `${minutes} min read`;
}
