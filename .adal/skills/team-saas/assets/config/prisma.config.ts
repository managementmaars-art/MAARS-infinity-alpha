import path from "path";
import dotenv from "dotenv";

/**
 * Prisma Configuration
 * 
 * File: prisma.config.ts (project root)
 * 
 * Loads environment variables for Prisma CLI operations.
 * Loads .env.local first (for secrets), then .env (for public vars).
 */

// Load .env.local first (contains secrets)
dotenv.config({ path: path.resolve(process.cwd(), ".env.local") });
// Then load .env (public vars, may be committed)
dotenv.config({ path: path.resolve(process.cwd(), ".env") });

export default {};
