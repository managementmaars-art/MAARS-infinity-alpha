#!/bin/bash
#
# Blog Infrastructure Setup Script
#
# Usage: bash setup-blog.sh [project-path]
#
# This script sets up the blog infrastructure for a Vite/React project.
# For Next.js projects, adjust imports accordingly.

set -e

PROJECT_PATH="${1:-.}"
SKILL_PATH="$(dirname "$(dirname "$(realpath "$0")")")"

echo "🚀 Setting up blog infrastructure..."
echo "   Project: $PROJECT_PATH"
echo "   Skill: $SKILL_PATH"

# Create directories
echo "📁 Creating directories..."
mkdir -p "$PROJECT_PATH/src/content/blog"
mkdir -p "$PROJECT_PATH/src/types"
mkdir -p "$PROJECT_PATH/src/lib"
mkdir -p "$PROJECT_PATH/src/components/blog"

# Copy types
echo "📝 Copying type definitions..."
cp "$SKILL_PATH/templates/blog-types.ts" "$PROJECT_PATH/src/types/blog.ts"

# Copy utilities
echo "📝 Copying utility functions..."
cp "$SKILL_PATH/templates/blog-utils.ts" "$PROJECT_PATH/src/lib/blog.ts"

# Copy components
echo "📝 Copying components..."
cp "$SKILL_PATH/components/blog-card.tsx" "$PROJECT_PATH/src/components/blog/blog-card.tsx"
cp "$SKILL_PATH/components/blog-layout.tsx" "$PROJECT_PATH/src/components/blog/blog-layout.tsx"

# Create index export
cat > "$PROJECT_PATH/src/components/blog/index.ts" << 'EOF'
export * from './blog-card';
export * from './blog-layout';
EOF

# Copy pattern images if they exist
echo "🖼️  Checking for pattern images..."
if [ -d "$SKILL_PATH/patterns" ]; then
  for pattern in "$SKILL_PATH/patterns"/*.png; do
    if [ -f "$pattern" ]; then
      cp "$pattern" "$PROJECT_PATH/public/"
      echo "   Copied: $(basename "$pattern")"
    fi
  done
else
  echo "   ⚠️  No pattern images found. Generate them manually using prompts in patterns/prompts.md"
fi

# Create sample article
echo "📝 Creating sample article..."
mkdir -p "$PROJECT_PATH/src/content/blog/getting-started"
cat > "$PROJECT_PATH/src/content/blog/getting-started/index.mdx" << 'EOF'
export const frontmatter = {
  title: "Getting Started with Our Blog",
  description: "Welcome to our blog! Learn how to write and publish articles.",
  date: "2026-01-30",
  author: "Your Team",
  tags: ["getting-started"],
  readingTime: 3,
  image: "/blog-pattern-1.png"
};

## Welcome!

This is your first blog post. Edit this file to get started.

## How to Add New Posts

1. Create a folder in `src/content/blog/your-slug/`
2. Add an `index.mdx` file with frontmatter
3. Write your content in Markdown
4. The post will automatically appear in the blog listing

## Frontmatter Fields

- **title**: SEO title (under 60 characters)
- **description**: Meta description (150-160 characters)
- **date**: Publication date (YYYY-MM-DD)
- **author**: Author name
- **tags**: Array of category tags
- **readingTime**: Estimated reading time in minutes
- **image**: Path to header image

Happy writing!
EOF

echo ""
echo "✅ Blog infrastructure setup complete!"
echo ""
echo "Next steps:"
echo "1. Add blog routes to your router"
echo "2. Generate pattern images using prompts in patterns/prompts.md"
echo "3. Update imports in copied files to match your project structure"
echo "4. Test at /blog"
EOF
