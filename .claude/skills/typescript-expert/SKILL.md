---
name: typescript-expert
description: TypeScript expert patterns — advanced types, generics, decorators, utility types, Zod validation, strict mode, monorepos for MAARS TypeScript agents
---

# TypeScript Expert — MAARS Reference

## Advanced Type Patterns
```typescript
// Template literal types
type EventName = `on${Capitalize<string>}`;
type ApiRoute = `/api/${string}`;
type CSSProperty = `${string}-${string}`;

// Conditional types
type NonNullable<T> = T extends null | undefined ? never : T;
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type Awaited<T> = T extends Promise<infer U> ? Awaited<U> : T;

// Mapped types
type Optional<T> = { [K in keyof T]?: T[K] };
type ReadOnly<T> = { readonly [K in keyof T]: T[K] };
type Nullable<T> = { [K in keyof T]: T[K] | null };
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// Discriminated unions
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

type Action =
  | { type: "LOGIN"; payload: { email: string } }
  | { type: "LOGOUT" }
  | { type: "UPDATE_USER"; payload: Partial<User> };
```

## Generics
```typescript
// Generic constraints
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Generic with default
interface ApiResponse<T = unknown> {
  data: T;
  status: number;
  message: string;
}

// Builder pattern with generics
class QueryBuilder<T extends Record<string, unknown>> {
  private filters: Partial<T> = {};
  
  where<K extends keyof T>(key: K, value: T[K]): this {
    this.filters[key] = value;
    return this;
  }
  
  build(): Partial<T> { return this.filters; }
}

// Curried generic function
const createReducer = <S, A>(
  handlers: { [K in A extends { type: infer T } ? T : never]:
    (state: S, action: Extract<A, { type: K }>) => S }
) => (state: S, action: A) => {
  const handler = (handlers as any)[(action as any).type];
  return handler ? handler(state, action) : state;
};
```

## Zod Validation
```typescript
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  age: z.number().min(0).max(150),
  role: z.enum(["admin", "user", "guest"]),
  createdAt: z.coerce.date(),
  metadata: z.record(z.string(), z.unknown()).optional(),
});

type User = z.infer<typeof UserSchema>;

// Parse with error handling
const parseUser = (data: unknown): Result<User> => {
  const result = UserSchema.safeParse(data);
  if (!result.success) {
    return { success: false, error: new Error(result.error.message) };
  }
  return { success: true, data: result.data };
};

// Nested schemas
const OrderSchema = z.object({
  items: z.array(z.object({
    productId: z.string(),
    quantity: z.number().positive(),
    price: z.number().positive(),
  })).min(1),
  total: z.number().positive(),
  user: UserSchema.pick({ id: true, email: true }),
}).refine(
  (data) => data.items.reduce((sum, i) => sum + i.price * i.quantity, 0) === data.total,
  { message: "Total doesn't match items" }
);
```

## Utility Types Reference
```typescript
// Built-in utilities
type P = Partial<User>;          // All optional
type R = Required<User>;         // All required
type RO = Readonly<User>;        // All readonly
type Pick<T, K> = ...            // Pick specific keys
type Omit<T, K> = ...            // Remove specific keys
type Record<K, V> = ...          // Map type
type Exclude<T, U> = ...         // Remove from union
type Extract<T, U> = ...         // Keep from union
type NonNullable<T> = ...        // Remove null/undefined
type ReturnType<T> = ...         // Function return type
type Parameters<T> = ...         // Function parameters
type ConstructorParameters<T> = // Constructor params
type InstanceType<T> = ...       // Class instance type

// Custom utilities
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

type Prettify<T> = { [K in keyof T]: T[K] } & {};

type UnionToIntersection<U> =
  (U extends any ? (x: U) => void : never) extends (x: infer I) => void ? I : never;
```

## Declaration Merging & Module Augmentation
```typescript
// Extend third-party types
declare module "express" {
  interface Request {
    user?: { id: string; role: string };
  }
}

// Extend global types
declare global {
  interface Window {
    analytics: AnalyticsInstance;
  }
}

// Augment existing interface
interface Array<T> {
  groupBy<K extends keyof T>(key: K): Record<string, T[]>;
}
```

## tsconfig Best Practices
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "verbatimModuleSyntax": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

## Models to Use
- **TypeScript code generation**: `claude-opus-4-6` (best TS type inference)
- **Type system design**: `claude-opus-4-6`
- **Refactoring to strict TS**: `claude-sonnet-4-6`
