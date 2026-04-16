import { PrismaClient } from "@/generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";

/**
 * Lazy-loaded Prisma client with connection pooling
 * 
 * Features:
 * - Uses @prisma/adapter-pg with raw pg.Pool (Prisma 7+ driver adapter pattern)
 * - Schema versioning for dev hot-reload
 * - Proxy pattern for lazy initialization
 * - Generated client goes to src/generated/prisma (not node_modules)
 * 
 * Required packages:
 *   bun add @prisma/client @prisma/adapter-pg pg
 *   bun add -D prisma
 */

// Schema version - increment when schema changes to invalidate cached client
const SCHEMA_VERSION = 1;

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
  pool: Pool | undefined;
  schemaVersion: number | undefined;
};

function createPrismaClient(): PrismaClient {
  const connectionString = process.env.DATABASE_URL;
  if (!connectionString) {
    throw new Error("DATABASE_URL environment variable is not set");
  }
  
  // Create connection pool
  const pool = globalForPrisma.pool ?? new Pool({ connectionString });
  const adapter = new PrismaPg(pool);
  
  // Cache pool in dev to prevent connection exhaustion
  if (process.env.NODE_ENV !== "production") {
    globalForPrisma.pool = pool;
  }
  
  return new PrismaClient({ adapter });
}

// Lazy initialization - only create client on first access
function getPrismaClient(): PrismaClient {
  const needsNewClient = 
    !globalForPrisma.prisma || 
    globalForPrisma.schemaVersion !== SCHEMA_VERSION;

  if (needsNewClient) {
    const instance = createPrismaClient();
    if (process.env.NODE_ENV !== "production") {
      globalForPrisma.prisma = instance;
      globalForPrisma.schemaVersion = SCHEMA_VERSION;
    }
    return instance;
  }
  
  return globalForPrisma.prisma!;
}

// Export getter for lazy access via Proxy
// This ensures the client is only created when actually used
export const prisma = new Proxy({} as PrismaClient, {
  get(_target, prop) {
    return getPrismaClient()[prop as keyof PrismaClient];
  },
});
