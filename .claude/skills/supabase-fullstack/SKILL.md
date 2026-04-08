---
name: supabase-fullstack
description: Supabase — Auth, Postgres, Realtime, Storage, Edge Functions, RLS policies, React integration for MAARS fullstack agents
---

# Supabase Fullstack — MAARS Reference

## Setup & Client
```typescript
import { createClient } from "@supabase/supabase-js";
import type { Database } from "./database.types";  // generated types

const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Server-side with service role (admin)
const supabaseAdmin = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!  // Never expose to client!
);
```

## Auth
```typescript
// Sign up
const { data, error } = await supabase.auth.signUp({
  email, password,
  options: { data: { full_name: name } },
});

// Sign in
const { data: { session } } = await supabase.auth.signInWithPassword({ email, password });

// OAuth
await supabase.auth.signInWithOAuth({ provider: "google",
  options: { redirectTo: `${window.location.origin}/auth/callback` } });

// Session
const { data: { session } } = await supabase.auth.getSession();
const { data: { user } } = await supabase.auth.getUser();

// Listen to auth changes
supabase.auth.onAuthStateChange((event, session) => {
  if (event === "SIGNED_IN") updateUser(session?.user);
  if (event === "SIGNED_OUT") clearUser();
});

// Sign out
await supabase.auth.signOut();
```

## Database Queries
```typescript
// Select with filters
const { data, error } = await supabase
  .from("posts")
  .select("*, author:profiles(id, name, avatar_url)")
  .eq("status", "published")
  .gte("created_at", new Date(Date.now() - 7 * 86400000).toISOString())
  .order("created_at", { ascending: false })
  .range(0, 9);  // pagination

// Insert
const { data: post, error } = await supabase
  .from("posts")
  .insert({ title, content, author_id: user.id })
  .select()
  .single();

// Update
await supabase.from("profiles")
  .update({ avatar_url: url })
  .eq("id", user.id);

// Upsert
await supabase.from("settings")
  .upsert({ user_id: user.id, theme: "dark" }, { onConflict: "user_id" });

// Delete
await supabase.from("comments").delete().eq("id", commentId);

// RPC (stored procedure)
const { data } = await supabase.rpc("increment_likes", { post_id: id });
```

## Row Level Security (RLS)
```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own posts
CREATE POLICY "users_own_posts" ON posts
  FOR ALL USING (auth.uid() = user_id);

-- Everyone can read published posts
CREATE POLICY "public_posts" ON posts
  FOR SELECT USING (status = 'published');

-- Only owners can update
CREATE POLICY "owner_update" ON posts
  FOR UPDATE USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Admin role bypass
CREATE POLICY "admin_all" ON posts
  FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- Access current user's JWT claims
SELECT auth.uid();        -- user UUID
SELECT auth.role();       -- role (authenticated/anon)
SELECT auth.jwt();        -- full JWT payload
```

## Realtime
```typescript
// Subscribe to table changes
const channel = supabase
  .channel("public:posts")
  .on("postgres_changes", {
    event: "*",  // INSERT | UPDATE | DELETE | *
    schema: "public",
    table: "posts",
    filter: `author_id=eq.${user.id}`,
  }, (payload) => {
    if (payload.eventType === "INSERT") addPost(payload.new);
    if (payload.eventType === "UPDATE") updatePost(payload.new);
    if (payload.eventType === "DELETE") removePost(payload.old.id);
  })
  .subscribe();

// Presence (who's online)
const presenceChannel = supabase.channel("room:lobby");
await presenceChannel.track({ user_id: user.id, online_at: new Date() });
presenceChannel.on("presence", { event: "sync" }, () => {
  const state = presenceChannel.presenceState();
  setOnlineUsers(Object.values(state).flat());
});

// Cleanup
supabase.removeChannel(channel);
```

## Storage
```typescript
// Upload file
const { data, error } = await supabase.storage
  .from("avatars")
  .upload(`${user.id}/avatar.jpg`, file, {
    cacheControl: "3600",
    upsert: true,
    contentType: "image/jpeg",
  });

// Get public URL
const { data: { publicUrl } } = supabase.storage
  .from("avatars")
  .getPublicUrl(`${user.id}/avatar.jpg`);

// Signed URL (private bucket)
const { data: { signedUrl } } = await supabase.storage
  .from("private-docs")
  .createSignedUrl("doc.pdf", 3600);  // expires in 1 hour

// Delete
await supabase.storage.from("avatars").remove([`${user.id}/avatar.jpg`]);
```

## Edge Functions
```typescript
// supabase/functions/send-email/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    { auth: { persistSession: false } }
  );
  
  const { email } = await req.json();
  // ... send email logic
  
  return new Response(JSON.stringify({ sent: true }), {
    headers: { "Content-Type": "application/json" },
  });
});

// Call from client
const { data, error } = await supabase.functions.invoke("send-email", {
  body: { email: "user@example.com" },
});
```

## Generate TypeScript Types
```bash
npx supabase gen types typescript --project-id YOUR_PROJECT_ID > src/database.types.ts
```

## Models to Use
- **Schema design + RLS policies**: `claude-sonnet-4-6`
- **Complex queries**: `claude-opus-4-6`
- **Edge Functions**: `claude-sonnet-4-6`
