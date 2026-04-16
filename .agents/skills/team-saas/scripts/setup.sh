#!/bin/bash

# ===========================================
# Team SaaS Quick Setup Script
# ===========================================
# 
# This script helps set up a new team SaaS project.
# Run from your project root after `create-next-app`.
#
# Usage:
#   bash ~/.cursor/skills/team-saas/scripts/setup.sh

set -e

echo "🚀 Team SaaS Setup"
echo "=================="

# Check if bun is available
if ! command -v bun &> /dev/null; then
    echo "❌ Bun is required. Install from: https://bun.sh"
    exit 1
fi

# ===========================================
# 1. Install Dependencies
# ===========================================
echo ""
echo "📦 Installing dependencies..."

# Core auth & database
bun add next-auth@beta @auth/prisma-adapter bcryptjs
bun add @prisma/client @prisma/adapter-pg pg
bun add -D prisma @types/bcryptjs

# UI
bun add lucide-react
bun add next-themes class-variance-authority clsx tailwind-merge
bun add @tanstack/react-query

# Validation (Zod 4.x)
bun add zod

# Email
bun add resend

# Storage
bun add @aws-sdk/client-s3 @aws-sdk/s3-request-presigner

# Jobs
bun add pg-boss

# Dotenv for prisma config
bun add dotenv

echo "✅ Dependencies installed"

# ===========================================
# 2. Initialize shadcn/ui
# ===========================================
echo ""
echo "🎨 Setting up shadcn/ui..."

# Initialize shadcn with new-york style
bunx shadcn@latest init -y --style new-york --base-color neutral

# Add essential components
bunx shadcn@latest add button card dialog input label sonner tooltip dropdown-menu avatar badge form command popover separator sheet

echo "✅ shadcn/ui configured"

# ===========================================
# 3. Initialize Prisma
# ===========================================
echo ""
echo "🗄️  Setting up Prisma..."

# Initialize if schema doesn't exist
if [ ! -f "prisma/schema.prisma" ]; then
    bunx prisma init
fi

echo "✅ Prisma initialized"

# ===========================================
# 4. Create directories
# ===========================================
echo ""
echo "📁 Creating directories..."

mkdir -p src/lib/jobs
mkdir -p src/hooks
mkdir -p src/types
mkdir -p src/generated/prisma
mkdir -p src/components/teams
mkdir -p src/components/invitations
mkdir -p src/components/shared
mkdir -p "src/app/(auth)/login"
mkdir -p "src/app/(auth)/register"
mkdir -p "src/app/(auth)/forgot-password"
mkdir -p "src/app/(dashboard)/teams/[teamId]"
mkdir -p "src/app/api/auth/[...nextauth]"
mkdir -p "src/app/api/auth/register"
mkdir -p "src/app/api/auth/forgot-password"
mkdir -p "src/app/api/teams/[teamId]/invitations/[invitationId]"
mkdir -p "src/app/api/teams/[teamId]/members/[memberId]"
mkdir -p "src/app/api/invitations/[token]/accept"
mkdir -p "src/app/api/uploads/[...path]"
mkdir -p "src/app/invite/[token]"
mkdir -p scripts

echo "✅ Directories created"

# ===========================================
# 5. Create .env.example
# ===========================================
echo ""
echo "🔐 Creating .env.example..."

cat > .env.example << 'EOF'
# Database
DATABASE_URL="postgresql://postgres:password@localhost:5432/myapp"

# Auth
AUTH_SECRET="generate-with-openssl-rand-base64-32"
NEXTAUTH_URL="http://localhost:3000"

# Email
RESEND_API_KEY="re_your_key"
EMAIL_FROM="onboarding@resend.dev"

# S3 Storage (Railway)
AWS_ENDPOINT_URL="https://..."
AWS_ACCESS_KEY_ID="..."
AWS_SECRET_ACCESS_KEY="..."
AWS_S3_BUCKET_NAME="..."
AWS_DEFAULT_REGION="auto"

# App
NEXT_PUBLIC_APP_NAME="My SaaS"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
EOF

echo "✅ .env.example created"

# ===========================================
# 6. Create prisma.config.ts
# ===========================================
echo ""
echo "📝 Creating prisma.config.ts..."

cat > prisma.config.ts << 'EOF'
import path from "path";
import dotenv from "dotenv";

// Load .env.local first (secrets), then .env (public vars)
dotenv.config({ path: path.resolve(process.cwd(), ".env.local") });
dotenv.config({ path: path.resolve(process.cwd(), ".env") });

export default {};
EOF

echo "✅ prisma.config.ts created"

# ===========================================
# Done!
# ===========================================
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env.local and fill in values"
echo "  2. Copy template files from ~/.cursor/skills/team-saas/assets/"
echo "  3. Update prisma/schema.prisma:"
echo "     - Change generator to: provider = \"prisma-client\""
echo "     - Set output to: output = \"../src/generated/prisma\""
echo "  4. Run: bunx prisma db push && bunx prisma generate"
echo "  5. Start dev server: bun dev"
echo ""
echo "Template files to copy:"
echo "  - assets/lib/* → src/lib/"
echo "  - assets/components/* → src/components/"
echo "  - assets/hooks/* → src/hooks/"
echo "  - assets/types/* → src/types/"
echo "  - assets/api/* → src/app/api/ (adjust paths)"
echo "  - assets/config/proxy.ts → src/proxy.ts"
echo "  - assets/config/next.config.ts → next.config.ts"
echo "  - assets/config/globals.css → src/app/globals.css"
echo "  - assets/prisma/schema.prisma → prisma/schema.prisma"
