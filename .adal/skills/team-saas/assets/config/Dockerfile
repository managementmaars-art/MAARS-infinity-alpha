# ===========================================
# Team SaaS Dockerfile
# Single container: Next.js + pg-boss worker
# ===========================================
# 
# Node 22 Alpine base + Bun for fast package management
# Runs both Next.js server and pg-boss worker in one container

FROM node:22-alpine AS base

# Install dependencies for native modules
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Install bun globally (faster than npm)
RUN npm install -g bun

# Copy package files and prisma schema (needed for postinstall)
COPY package.json bun.lock* ./
COPY prisma ./prisma/
COPY prisma.config.ts ./

# Install dependencies (postinstall runs prisma generate)
RUN bun install --frozen-lockfile

# Copy source code
# Note: .env is copied for build-time public vars (NEXT_PUBLIC_*)
# Private keys should be in .env.local (gitignored) and set via Railway
COPY . .

# Build Next.js app
RUN bun run build

# Create startup script that runs both processes
# - pg-boss worker for background jobs
# - Next.js server for the web app
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'echo "Starting pg-boss worker..."' >> /app/start.sh && \
    echo 'bun run scripts/worker.ts &' >> /app/start.sh && \
    echo 'WORKER_PID=$!' >> /app/start.sh && \
    echo 'echo "Starting Next.js server..."' >> /app/start.sh && \
    echo 'bun run start &' >> /app/start.sh && \
    echo 'NEXT_PID=$!' >> /app/start.sh && \
    echo 'trap "kill $WORKER_PID $NEXT_PID 2>/dev/null" EXIT' >> /app/start.sh && \
    echo 'wait' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 3000

# Run both processes
CMD ["/app/start.sh"]
