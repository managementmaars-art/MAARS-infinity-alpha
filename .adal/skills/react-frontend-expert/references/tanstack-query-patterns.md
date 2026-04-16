# TanStack Query Patterns

CRUD operation patterns, query key conventions, cache invalidation, and optimistic updates for TanStack Query v5 with React.

---

## Query Key Conventions

Structure query keys hierarchically for targeted invalidation:

```tsx
// All users (list)
["users"]

// Single user
["users", userId]

// Filtered user list
["users", { q: "search", role: "admin", page: 1 }]

// User's posts (nested resource)
["users", userId, "posts"]

// Single post
["posts", postId]
```

**Rules:**
- First element is the resource name (string)
- Subsequent elements narrow the scope (ids, filters)
- Object filters should be normalized (same key order)
- Use `queryOptions()` factory to prevent key duplication

---

## Query Options Factory

Centralize all query definitions per resource:

```tsx
// api/users.ts
import { queryOptions } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { User, UserListResponse } from "@/types/user";

interface UserListParams {
  q?: string;
  cursor?: string | null;
  limit?: number;
}

export const userQueries = {
  all: () =>
    queryOptions({
      queryKey: ["users"] as const,
      queryFn: () => apiClient.get<UserListResponse>("/users"),
      staleTime: 5 * 60 * 1000, // 5 minutes
    }),

  list: (params: UserListParams) =>
    queryOptions({
      queryKey: ["users", params] as const,
      queryFn: () =>
        apiClient.get<UserListResponse>("/users", { params }),
      staleTime: 2 * 60 * 1000,
    }),

  detail: (userId: number) =>
    queryOptions({
      queryKey: ["users", userId] as const,
      queryFn: () => apiClient.get<User>(`/users/${userId}`),
      staleTime: 5 * 60 * 1000,
    }),
};
```

**Usage in components:**
```tsx
// Clean and type-safe — no key duplication
const { data } = useQuery(userQueries.detail(42));
const { data } = useQuery(userQueries.list({ q: search }));
```

---

## CRUD Operations

### Create (useMutation + invalidate)

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import type { UserCreate, User } from "@/types/user";

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UserCreate) =>
      apiClient.post<User>("/users", data),

    onSuccess: () => {
      // Invalidate all user lists — they're now stale
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

// Usage in component
function CreateUserButton() {
  const createUser = useCreateUser();

  const handleClick = () => {
    createUser.mutate(
      { email: "new@example.com", displayName: "New User" },
      {
        onSuccess: (user) => {
          toast.success(`Created ${user.displayName}`);
        },
        onError: (error) => {
          toast.error(error.message);
        },
      },
    );
  };

  return (
    <button onClick={handleClick} disabled={createUser.isPending}>
      {createUser.isPending ? "Creating..." : "Create User"}
    </button>
  );
}
```

### Update (useMutation + invalidate specific)

```tsx
export function useUpdateUser(userId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UserPatch) =>
      apiClient.patch<User>(`/users/${userId}`, data),

    onSuccess: (updatedUser) => {
      // Update the specific user in cache
      queryClient.setQueryData(["users", userId], updatedUser);
      // Invalidate lists (they may be sorted/filtered differently)
      queryClient.invalidateQueries({ queryKey: ["users"], exact: false });
    },
  });
}
```

### Delete (useMutation + remove from cache)

```tsx
export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) =>
      apiClient.delete(`/users/${userId}`),

    onSuccess: (_, userId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: ["users", userId] });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}
```

---

## Optimistic Updates

Update the UI immediately, rollback on error:

```tsx
export function useToggleFavorite(postId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiClient.post(`/posts/${postId}/favorite`),

    onMutate: async () => {
      // Cancel outgoing queries to prevent race conditions
      await queryClient.cancelQueries({ queryKey: ["posts", postId] });

      // Snapshot current state for rollback
      const previousPost = queryClient.getQueryData<Post>(["posts", postId]);

      // Optimistically update
      queryClient.setQueryData<Post>(["posts", postId], (old) =>
        old ? { ...old, isFavorited: !old.isFavorited } : old,
      );

      return { previousPost };
    },

    onError: (_err, _vars, context) => {
      // Rollback on error
      if (context?.previousPost) {
        queryClient.setQueryData(["posts", postId], context.previousPost);
      }
    },

    onSettled: () => {
      // Always refetch to sync with server
      queryClient.invalidateQueries({ queryKey: ["posts", postId] });
    },
  });
}
```

---

## Infinite Scroll

```tsx
import { useInfiniteQuery } from "@tanstack/react-query";

export function useInfinitePosts() {
  return useInfiniteQuery({
    queryKey: ["posts", "infinite"],
    queryFn: ({ pageParam }) =>
      apiClient.get<PostListResponse>("/posts", {
        params: { cursor: pageParam, limit: 20 },
      }),
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.hasMore ? lastPage.nextCursor : undefined,
    staleTime: 2 * 60 * 1000,
  });
}

// Usage
function PostFeed() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfinitePosts();

  const allPosts = data?.pages.flatMap((page) => page.items) ?? [];

  return (
    <div>
      {allPosts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
      {hasNextPage && (
        <button onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
          {isFetchingNextPage ? "Loading..." : "Load More"}
        </button>
      )}
    </div>
  );
}
```

---

## Dependent Queries

Query that depends on another query's result:

```tsx
function UserPosts({ userId }: { userId: number }) {
  // First query: get user
  const { data: user } = useQuery(userQueries.detail(userId));

  // Second query: depends on user data
  const { data: posts } = useQuery({
    queryKey: ["users", userId, "posts", user?.preferredCategory],
    queryFn: () =>
      apiClient.get(`/users/${userId}/posts`, {
        params: { category: user!.preferredCategory },
      }),
    enabled: !!user, // Only run when user data is available
  });

  // ...
}
```

---

## Global Configuration

```tsx
// main.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,    // 5 minutes (avoid staleTime: 0)
      gcTime: 10 * 60 * 1000,       // 10 minutes garbage collection
      retry: 1,                      // Retry once on failure
      refetchOnWindowFocus: false,   // Disable aggressive refetching
    },
    mutations: {
      retry: 0,                      // No retry for mutations
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```
