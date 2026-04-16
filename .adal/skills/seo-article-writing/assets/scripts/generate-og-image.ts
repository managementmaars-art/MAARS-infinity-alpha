/**
 * Dynamic OG Image Generation Script
 * 
 * This script generates Open Graph images programmatically by:
 * 1. Loading a pattern background image
 * 2. Overlaying article title, description, and branding
 * 3. Exporting as optimized PNG
 * 
 * Requirements:
 * - Node.js with canvas support (@napi-rs/canvas or node-canvas)
 * - Pattern images in public/ folder
 * 
 * Usage:
 * ```bash
 * bun run scripts/generate-og-image.ts --title="Article Title" --pattern=1
 * ```
 */

import { createCanvas, loadImage, GlobalFonts } from '@napi-rs/canvas';
import { writeFileSync, existsSync } from 'fs';
import { join } from 'path';

// Configuration
const CONFIG = {
  width: 1200,
  height: 630,
  padding: 60,
  fonts: {
    title: {
      family: 'Inter',
      size: 56,
      weight: 700,
      lineHeight: 1.2,
    },
    description: {
      family: 'Inter',
      size: 24,
      weight: 400,
      lineHeight: 1.4,
    },
    brand: {
      family: 'Inter',
      size: 20,
      weight: 600,
    },
  },
  colors: {
    text: '#ffffff',
    textMuted: 'rgba(255, 255, 255, 0.7)',
    primary: '#f97316',
    overlay: 'rgba(0, 0, 0, 0.4)',
  },
};

interface OGImageOptions {
  title: string;
  description?: string;
  pattern: 1 | 2 | 3;
  outputPath: string;
  brandName?: string;
  brandLogo?: string;
}

/**
 * Wrap text to fit within a maximum width
 */
function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number
): string[] {
  const words = text.split(' ');
  const lines: string[] = [];
  let currentLine = '';

  for (const word of words) {
    const testLine = currentLine ? `${currentLine} ${word}` : word;
    const metrics = ctx.measureText(testLine);
    
    if (metrics.width > maxWidth && currentLine) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  }
  
  if (currentLine) {
    lines.push(currentLine);
  }
  
  return lines;
}

/**
 * Generate an OG image with the given options
 */
export async function generateOGImage(options: OGImageOptions): Promise<void> {
  const {
    title,
    description,
    pattern,
    outputPath,
    brandName = 'Open Sunsama',
  } = options;

  // Create canvas
  const canvas = createCanvas(CONFIG.width, CONFIG.height);
  const ctx = canvas.getContext('2d');

  // Load and draw background pattern
  const patternPath = join(process.cwd(), 'public', `blog-pattern-${pattern}.png`);
  
  if (existsSync(patternPath)) {
    const background = await loadImage(patternPath);
    ctx.drawImage(background, 0, 0, CONFIG.width, CONFIG.height);
  } else {
    // Fallback: solid dark background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, CONFIG.width, CONFIG.height);
  }

  // Add semi-transparent overlay for text readability
  ctx.fillStyle = CONFIG.colors.overlay;
  ctx.fillRect(0, 0, CONFIG.width, CONFIG.height);

  // Draw title
  ctx.fillStyle = CONFIG.colors.text;
  ctx.font = `${CONFIG.fonts.title.weight} ${CONFIG.fonts.title.size}px ${CONFIG.fonts.title.family}`;
  
  const maxTitleWidth = CONFIG.width - (CONFIG.padding * 2);
  const titleLines = wrapText(ctx, title, maxTitleWidth);
  const titleLineHeight = CONFIG.fonts.title.size * CONFIG.fonts.title.lineHeight;
  
  let y = CONFIG.height / 2 - ((titleLines.length * titleLineHeight) / 2);
  
  // Adjust Y if we have description
  if (description) {
    y -= 40;
  }

  for (const line of titleLines) {
    ctx.fillText(line, CONFIG.padding, y);
    y += titleLineHeight;
  }

  // Draw description (if provided)
  if (description) {
    ctx.fillStyle = CONFIG.colors.textMuted;
    ctx.font = `${CONFIG.fonts.description.weight} ${CONFIG.fonts.description.size}px ${CONFIG.fonts.description.family}`;
    
    const descLines = wrapText(ctx, description, maxTitleWidth);
    y += 20; // Gap between title and description
    
    for (const line of descLines.slice(0, 2)) { // Max 2 lines
      ctx.fillText(line, CONFIG.padding, y);
      y += CONFIG.fonts.description.size * CONFIG.fonts.description.lineHeight;
    }
  }

  // Draw brand name at bottom
  ctx.fillStyle = CONFIG.colors.primary;
  ctx.font = `${CONFIG.fonts.brand.weight} ${CONFIG.fonts.brand.size}px ${CONFIG.fonts.brand.family}`;
  ctx.fillText(brandName, CONFIG.padding, CONFIG.height - CONFIG.padding);

  // Draw decorative line
  ctx.strokeStyle = CONFIG.colors.primary;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(CONFIG.padding, CONFIG.height - CONFIG.padding - 30);
  ctx.lineTo(CONFIG.padding + 60, CONFIG.height - CONFIG.padding - 30);
  ctx.stroke();

  // Export to PNG
  const buffer = canvas.toBuffer('image/png');
  writeFileSync(outputPath, buffer);
  
  console.log(`✅ Generated OG image: ${outputPath}`);
}

/**
 * CLI entry point
 */
async function main() {
  const args = process.argv.slice(2);
  
  const getArg = (name: string): string | undefined => {
    const arg = args.find(a => a.startsWith(`--${name}=`));
    return arg?.split('=')[1];
  };

  const title = getArg('title');
  const description = getArg('description');
  const pattern = parseInt(getArg('pattern') || '1') as 1 | 2 | 3;
  const output = getArg('output') || 'public/og-image.png';

  if (!title) {
    console.error('Usage: bun run generate-og-image.ts --title="Your Title" [--pattern=1] [--output=path]');
    process.exit(1);
  }

  await generateOGImage({
    title,
    description,
    pattern,
    outputPath: output,
  });
}

// Run if called directly
main().catch(console.error);

/**
 * Batch generation for all blog posts
 * 
 * Usage in build script:
 * ```typescript
 * import { generateOGImage } from './generate-og-image';
 * import { getAllBlogPosts } from '../lib/blog';
 * 
 * const posts = await getAllBlogPosts();
 * 
 * for (const post of posts) {
 *   await generateOGImage({
 *     title: post.title,
 *     description: post.description,
 *     pattern: getPatternForTags(post.tags),
 *     outputPath: `public/og/${post.slug}.png`,
 *   });
 * }
 * ```
 */
export async function generateAllOGImages(
  posts: Array<{ slug: string; title: string; description?: string; tags: string[] }>
): Promise<void> {
  const getPatternForTags = (tags: string[]): 1 | 2 | 3 => {
    if (tags.includes('comparison') || tags.includes('review')) return 1;
    if (tags.includes('guide') || tags.includes('tutorial')) return 2;
    return 3;
  };

  for (const post of posts) {
    await generateOGImage({
      title: post.title,
      description: post.description,
      pattern: getPatternForTags(post.tags),
      outputPath: `public/og/${post.slug}.png`,
    });
  }

  console.log(`✅ Generated ${posts.length} OG images`);
}
