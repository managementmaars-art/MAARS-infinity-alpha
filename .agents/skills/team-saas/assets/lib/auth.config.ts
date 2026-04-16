import type { NextAuthConfig } from "next-auth";
import Credentials from "next-auth/providers/credentials";

/**
 * Auth configuration for NextAuth v5
 * 
 * NOTE: Route protection is done via layout.tsx Server Components,
 * NOT via Edge middleware. The `authorized` callback below is included
 * for compatibility but is not actively used for route protection.
 * 
 * Protection happens in:
 * - src/app/(dashboard)/layout.tsx - Server-side session check
 * - API routes - Manual auth() calls with requireTeamMember()
 */
export const authConfig: NextAuthConfig = {
  // Trust the host header in production (Railway, Vercel, etc.)
  trustHost: true,
  
  providers: [
    // Credentials provider - actual authorization in auth.ts
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      // authorize is implemented in auth.ts (Node.js runtime with Prisma)
      authorize: () => null,
    }),
  ],
  
  callbacks: {
    // Enrich JWT token with user data
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.name = user.name;
        token.email = user.email;
        token.picture = user.image;
      }
      return token;
    },
    
    // Expose user data to client session
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.name = (token.name as string | undefined) ?? session.user.name;
        session.user.email = (token.email as string | undefined) ?? session.user.email;
        session.user.image = (token.picture as string | undefined) ?? session.user.image;
      }
      return session;
    },
  },
  
  pages: {
    signIn: "/login",
  },
  
  session: {
    strategy: "jwt",
  },
};
