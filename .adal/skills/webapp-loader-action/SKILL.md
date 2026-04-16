---
name: webapp-loader-action
description: >
  Create, update, or maintain React Router loaders and actions that call core use cases via the DI
  container in webapp packages (admin, client, or similar). Use this skill whenever the user wants
  to wire a route's loader or action to business logic, add data fetching to a route, handle a form
  submission that calls a use case, or update how a loader/action validates its inputs or maps its
  outputs. Trigger on: "add a loader for X", "create an action that does Y", "wire the use case to
  the route", "handle form submission for Z", "fetch data in the route", "add validation to the
  loader", or any time someone is connecting a web route to a core use case.
---

# Webapp Loader / Action Skill

Loaders fetch data for a route (called on GET). Actions handle mutations (called on POST/PUT/DELETE,
usually from a `<Form>` submission). Both live in the same route file and call use cases from the
core package through a DI container.

Read `references/templates.md` for copy-paste starting points.

## Before You Start

If the user hasn't told you which use case to call, **ask**. Then find the interface file:

```
{core-package}/src/useCase/{domain}/I{Name}.ts
```

Read it carefully — the input type tells you exactly what the use case expects, and the return type
tells you what you get back.

Key questions to clarify before writing code:
- **Loader or action (or both)?** Loaders = read data; actions = mutate.
- **Is the route behind auth?** If yes, extract a session token from the request.
- **Where does input come from?**
  - Loader: URL params (`args.params`) and/or query string (`new URL(args.request.url).searchParams`)
  - Action: URL params and/or request body — usually `FormData` (`await args.request.formData()`)
- **Does the action handle multiple intents?** A single action can dispatch on an `intent` field using a Zod discriminated union.
- **What does the caller (component) need back?** Shape the return value to be convenient for the component.

## Step 1 — Find the Use Case Interface

Grep or browse for `I{Name}.ts` in the core's `useCase/` directory. Read:
- The input type (and any auth wrapper like `WithOperatorAuth<…>`)
- The return type (usually `Result<DTO, Error>`)
- Any optional fields (like `populate`)

This tells you exactly which fields to validate and pass.

## Step 2 — Validate Inputs with Zod

Always validate before touching the use case. Use the simplest validator that captures the shape:

**Loader — query string:**
```ts
const query_validator = z.object({
  search: z.string().optional(),
  page_n: z.coerce.number().int().min(1).optional().default(1),
  page_size: z.coerce.number().int().min(10).max(100).optional().default(25),
  id: z.string().optional(),
});
```

**Loader — URL params:**
```ts
const params_validator = z.object({
  _id: z.string().min(1),
});
```

**Action — single intent:**
```ts
const body_validator = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
});
```

**Action — multiple intents (discriminated union):**
```ts
const body_validator = z.discriminatedUnion('intent', [
  z.object({ intent: z.literal('CREATE'), name: z.string().min(1) }),
  z.object({ intent: z.literal('DELETE'), id: z.string() }),
]);
```

Parse from `Object.fromEntries(…)` for both query strings and FormData. Use `.parse()` in loaders
(throw on error) or `.safeParse()` in actions (return an error response on failure).

## Step 3 — Authenticate

If the route is behind auth, call the appropriate helper at the top of the loader/action before
doing anything else. This will redirect or throw if the user isn't logged in.

```ts
// Example: operator session cookie
const session_id = await requireOperatorSessId(args.request);
```

The session token becomes part of the use case input (the auth wrapper field).

If the route is public, skip this step entirely.

## Step 4 — Get the Use Case and Execute

```ts
const result = await container
  .get<IMyUseCase>(Symbols.UseCase.myDomain.MyUseCaseName)
  .execute({
    session_id,        // from auth step
    ...validated,      // spread validated inputs
  });
```

Imports needed:
```ts
import { container, IMyUseCase, Symbols } from '@workspace/core';
```

Replace `@workspace` with the actual workspace name for the project (e.g. `@dav`, `@acme`).

## Step 5 — Handle the Result

**In a loader** — unwrap and throw on failure (React Router will catch it):
```ts
const data = result.unwrapOrThrow();
return { items: data };
```

Or handle specific errors gracefully:
```ts
if (result.isFailure()) throw new Response('Not found', { status: 404 });
return { item: result.data };
```

**In an action** — return a toast/response the component can consume:
```ts
// Using a Toast helper (if available in the project)
return Toast.fromResult(result, 'Created successfully');

// Or manually:
if (result.isFailure()) return { ok: false, error: result.error.message };
return { ok: true, data: result.data };
```

If validation fails in an action, return early:
```ts
const body = body_validator.safeParse(Object.fromEntries(await args.request.formData()));
if (!body.success) return { ok: false, error: 'Invalid input', details: body.error.flatten() };
```

## Step 6 — Transform the Return Value (if needed)

Shape the returned data to make life easy for the component. Common transforms:
- Build pagination links from page number and total
- Resolve a path/breadcrumb from a tree structure
- Merge multiple use case results into a flat object
- Compute derived boolean flags (`hasNext`, `isEmpty`, etc.)

Only add what the component actually needs. Keep it minimal.

## Checklist

- [ ] Use case interface read — input and return type understood
- [ ] Zod validator covers all inputs (params, query, or body)
- [ ] Auth called before any use case (if route is protected)
- [ ] Use case fetched from `container.get<I…>(Symbols.…)` — not instantiated directly
- [ ] Result handled: unwrapped in loaders, gracefully returned in actions
- [ ] Return value is flat and convenient for the component — no raw domain objects

## Special Cases

**Multiple use cases in one loader** — run them in parallel when they're independent:
```ts
const [aRes, bRes] = await Promise.all([
  container.get<IA>(Symbols.UseCase.foo.A).execute({ session_id }),
  container.get<IB>(Symbols.UseCase.bar.B).execute({ session_id }),
]);
const a = aRes.unwrapOrThrow();
const b = bRes.unwrapOrThrow();
```

**Optional data** — a use case may return `Maybe<T>` instead of `Result`. Use `.isSome()` / `.isNone()`:
```ts
const maybe = await container.get<IGetFoo>(Symbols.UseCase.foo.GetFoo).execute({ session_id, id });
const foo = maybe.isSome() ? maybe.data : null;
return { foo };
```

**Action with redirect** — after a mutation, redirect to the detail page:
```ts
const result = await container.get<ICreateFoo>(…).execute(…);
if (result.isFailure()) return { ok: false, error: result.error.message };
throw redirect(`/admin/foo/${result.data._id}`);
```

**Public loader (no auth)** — simply skip the auth step and pass only the validated input:
```ts
export async function loader(args: LoaderFunctionArgs) {
  const query = query_validator.parse(Object.fromEntries(new URL(args.request.url).searchParams));
  const result = await container.get<ISearchFoo>(Symbols.UseCase.foo.SearchFoo).execute(query);
  return { items: result.unwrapOrThrow() };
}
```

## Related Skills

- **`/usecase`**  — Create or update the use case being called
- **`/entity`**  — Create or update domain entities
