/**
 * MSW Handler Examples
 *
 * Mock Service Worker handler patterns for common API operations.
 * Import these in your test setup or override per-test.
 */
import { http, HttpResponse, delay } from "msw";

// ---------- CRUD Handlers ----------

// GET /api/users — List with pagination
const listUsers = http.get("/api/users", ({ request }) => {
  const url = new URL(request.url);
  const cursor = url.searchParams.get("cursor");
  const limit = Number(url.searchParams.get("limit") || "20");

  const allUsers = [
    { id: 1, displayName: "Alice", email: "alice@example.com", role: "admin" },
    { id: 2, displayName: "Bob", email: "bob@example.com", role: "member" },
    { id: 3, displayName: "Charlie", email: "charlie@example.com", role: "editor" },
  ];

  const startIndex = cursor ? allUsers.findIndex((u) => u.id > Number(cursor)) : 0;
  const items = allUsers.slice(startIndex, startIndex + limit);
  const hasMore = startIndex + limit < allUsers.length;

  return HttpResponse.json({
    items,
    next_cursor: hasMore ? String(items[items.length - 1].id) : null,
    has_more: hasMore,
  });
});

// GET /api/users/:id — Single user
const getUser = http.get("/api/users/:id", ({ params }) => {
  const userId = Number(params.id);
  const users: Record<number, object> = {
    1: { id: 1, displayName: "Alice", email: "alice@example.com", role: "admin" },
    2: { id: 2, displayName: "Bob", email: "bob@example.com", role: "member" },
  };

  const user = users[userId];
  if (!user) {
    return HttpResponse.json(
      { detail: `User ${userId} not found`, code: "NOT_FOUND" },
      { status: 404 },
    );
  }
  return HttpResponse.json(user);
});

// POST /api/users — Create user
const createUser = http.post("/api/users", async ({ request }) => {
  const body = (await request.json()) as Record<string, unknown>;
  return HttpResponse.json(
    {
      id: 99,
      ...body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    { status: 201 },
  );
});

// PATCH /api/users/:id — Update user
const updateUser = http.patch("/api/users/:id", async ({ params, request }) => {
  const body = (await request.json()) as Record<string, unknown>;
  return HttpResponse.json({
    id: Number(params.id),
    displayName: "Alice",
    email: "alice@example.com",
    ...body,
    updated_at: new Date().toISOString(),
  });
});

// DELETE /api/users/:id — Delete user
const deleteUser = http.delete("/api/users/:id", () => {
  return new HttpResponse(null, { status: 204 });
});

// ---------- Error Handlers ----------

// Simulate server error
const serverError = http.get("/api/users", () => {
  return HttpResponse.json(
    { detail: "Internal server error", code: "INTERNAL_ERROR" },
    { status: 500 },
  );
});

// Simulate validation error
const validationError = http.post("/api/users", () => {
  return HttpResponse.json(
    {
      detail: "Validation failed",
      code: "VALIDATION_ERROR",
      field_errors: [
        { field: "email", message: "Invalid email format", code: "INVALID_FORMAT" },
      ],
    },
    { status: 422 },
  );
});

// Simulate network delay
const slowResponse = http.get("/api/users", async () => {
  await delay(3000); // 3 second delay
  return HttpResponse.json({ items: [], next_cursor: null, has_more: false });
});

// ---------- Auth Handlers ----------

const login = http.post("/api/auth/login", async ({ request }) => {
  const body = (await request.json()) as { email: string; password: string };
  if (body.email === "admin@test.com" && body.password === "password") {
    return HttpResponse.json({
      access_token: "mock-jwt-token",
      token_type: "bearer",
    });
  }
  return HttpResponse.json(
    { detail: "Invalid credentials", code: "UNAUTHORIZED" },
    { status: 401 },
  );
});

const getCurrentUser = http.get("/api/auth/me", ({ request }) => {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return HttpResponse.json(
      { detail: "Not authenticated", code: "UNAUTHORIZED" },
      { status: 401 },
    );
  }
  return HttpResponse.json({
    id: 1,
    displayName: "Test Admin",
    email: "admin@test.com",
    role: "admin",
  });
});

// ---------- Export ----------

// Default handlers — use in setupServer
export const handlers = [
  listUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
  login,
  getCurrentUser,
];

// Error handlers — use with server.use() for specific tests
export const errorHandlers = {
  serverError,
  validationError,
  slowResponse,
};
