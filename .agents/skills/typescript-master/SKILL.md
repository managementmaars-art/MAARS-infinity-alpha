---
name: typescript-master
description: TypeScript language expert specializing in type system, generics, conditional types, and advanced patterns. Use when writing complex types, debugging type errors, or designing type-safe APIs.
---

# TypeScript Language Expert

Expert assistant for TypeScript type system mastery including generics, conditional types, mapped types, type inference, and advanced patterns.

## Thinking Process

When activated, follow this structured thinking approach to solve TypeScript type challenges:

### Step 1: Problem Classification

**Goal:** Understand what type of TypeScript challenge this is.

**Key Questions to Ask:**
- Is this a type design problem? (creating new types, modeling data)
- Is this a type error problem? (debugging, fixing type mismatches)
- Is this a type inference problem? (generics, conditional types)
- Is this a type safety problem? (runtime validation, narrowing)
- Is this a library typing problem? (third-party types, declaration files)

**Decision Point:** Classify to select appropriate approach:
- Type Design → Focus on modeling domain correctly
- Type Error → Trace the type mismatch source
- Type Inference → Design generics and constraints
- Type Safety → Add runtime validation with type guards
- Library Typing → Check @types packages, create declarations

### Step 2: Context Analysis

**Goal:** Understand the TypeScript environment and constraints.

**Key Questions to Ask:**
- What TypeScript version is in use? (5.0+ has new features)
- What is the strictness level? (strict, noUncheckedIndexedAccess, etc.)
- What is the module system? (ESM, CommonJS, bundler)
- Are there existing type patterns to follow?

**Actions:**
1. Check `tsconfig.json` for compiler options
2. Identify TypeScript version in `package.json`
3. Review existing type patterns in the codebase

**Version-Specific Features:**

| Feature | Minimum Version |
|---------|-----------------|
| Generics | 2.0 |
| Conditional Types | 2.8 |
| Template Literal Types | 4.1 |
| Const Type Parameters | 5.0 |
| satisfies Operator | 4.9 |

### Step 3: Type Design Principles

**Goal:** Apply TypeScript best practices to the solution.

**Thinking Framework - Core Principles:**

1. **Prefer Inference Over Annotation**
   - Let TypeScript infer when possible
   - Annotate function parameters, return types for public APIs
   - Use `satisfies` to check without widening

2. **Use `unknown` Over `any`**
   - `unknown` forces type checking before use
   - `any` disables all type checking
   - Exception: truly dynamic scenarios (rare)

3. **Discriminated Unions for Variants**
   - Use literal type discriminators
   - Enables exhaustive checking
   - Self-documenting code

4. **Narrow Types, Don't Widen**
   - Prefer `as const` for literal types
   - Use type guards to narrow
   - Avoid unnecessary type assertions

**Type Design Questions:**
- "What is the minimal type that describes this?"
- "Can TypeScript infer this, or must I annotate?"
- "Is this union exhaustive?"

### Step 4: Error Diagnosis

**Goal:** Systematically diagnose type errors.

**Thinking Framework:**
- "What does TypeScript expect vs what it received?"
- "Where did the unexpected type originate?"
- "Is this a structural or nominal mismatch?"

**Common Error Patterns:**

| Error Pattern | Likely Cause | Solution |
|--------------|--------------|----------|
| Type 'X' is not assignable to 'Y' | Missing property or wrong type | Add missing prop, fix type |
| Property does not exist | Optional prop or wrong union member | Add type guard, check optional |
| Type 'X' has no call signatures | Not a function type | Check function type |
| Argument not assignable to 'never' | Exhausted union without handling | Add missing case handler |

**Debugging Strategy:**
1. Hover over variables to see inferred types
2. Trace back to where the type was assigned
3. Check for implicit `any` (enable noImplicitAny)
4. Use `// @ts-expect-error` temporarily to isolate issues

### Step 5: Generic Type Design

**Goal:** Design reusable, type-safe generic functions and types.

**Thinking Framework:**
- "What type information flows through this function?"
- "What constraints are needed on the type parameter?"
- "Can I infer more than I'm currently inferring?"

**Generic Design Patterns:**

| Pattern | Use Case | Example |
|---------|----------|---------|
| Identity Generic | Preserve input type | `<T>(x: T) => T` |
| Constrained Generic | Limit to subset | `<T extends object>` |
| Mapped Type | Transform all props | `{ [K in keyof T]: ... }` |
| Conditional Type | Type-level branching | `T extends U ? X : Y` |
| Infer Keyword | Extract nested type | `T extends Promise<infer U> ? U : T` |

**Generic Best Practices:**
- Name parameters meaningfully (`TItem` not just `T`)
- Add constraints that document intent
- Provide defaults when sensible (`<T = string>`)
- Test with edge cases (empty arrays, undefined, etc.)

### Step 6: Type Narrowing Strategy

**Goal:** Safely narrow types for runtime operations.

**Thinking Framework:**
- "How do I know this is type X at runtime?"
- "What is the most reliable way to check?"
- "Does this narrowing work for TypeScript?"

**Narrowing Techniques:**

| Technique | Best For | Example |
|-----------|----------|---------|
| typeof | Primitives | `typeof x === 'string'` |
| instanceof | Class instances | `x instanceof Date` |
| in operator | Property presence | `'name' in x` |
| Discriminant | Tagged unions | `x.type === 'success'` |
| Custom guard | Complex objects | `function isUser(x): x is User` |
| Assertion function | Throw on invalid | `asserts x is User` |

**Type Guard Pattern:**
```typescript
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    typeof (obj as User).id === 'string'
  );
}
```

### Step 7: Advanced Type Patterns

**Goal:** Apply advanced patterns for complex scenarios.

**Thinking Framework:**
- "Is there a utility type that does this?"
- "Can I compose existing types?"
- "Is the type readable and maintainable?"

**Advanced Patterns:**

| Pattern | Purpose |
|---------|---------|
| Template Literal Types | String manipulation at type level |
| Recursive Types | Tree structures, nested objects |
| Branded Types | Nominal typing for primitives |
| Builder Pattern Types | Accumulate type information |

**Branded Type Example:**
```typescript
type UserId = string & { readonly __brand: unique symbol };

function createUserId(id: string): UserId {
  return id as UserId;
}

function fetchUser(id: UserId) { /* ... */ }

// Type error: string is not UserId
fetchUser("abc"); // Error!
fetchUser(createUserId("abc")); // OK
```

### Step 8: Validation and Testing

**Goal:** Ensure types are correct and maintainable.

**Type Testing Strategies:**
1. Use `@ts-expect-error` to test that invalid code fails
2. Create type test files with assertions
3. Use `Expect<Equal<A, B>>` utility for type assertions

**Type Test Pattern:**
```typescript
// Type tests (no runtime code)
type cases = [
  Expect<Equal<ReturnType<typeof fn>, string>>,
  Expect<Equal<Parameters<typeof fn>, [number, string]>>,
];

// Compile-time assertion utility
type Expect<T extends true> = T;
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends
  (<T>() => T extends Y ? 1 : 2) ? true : false;
```

**Maintainability Checklist:**
- [ ] Types are documented with JSDoc
- [ ] Complex types are broken into smaller pieces
- [ ] Type names are descriptive
- [ ] Exported types have explicit documentation

## Usage

### Run Type Check

```bash
bash /mnt/skills/user/typescript-master/scripts/type-check.sh [project-dir] [strict-mode]
```

**Arguments:**
- `project-dir` - Project directory (default: current directory)
- `strict-mode` - Enable strict checks: true/false (default: true)

**Examples:**
```bash
bash /mnt/skills/user/typescript-master/scripts/type-check.sh
bash /mnt/skills/user/typescript-master/scripts/type-check.sh ./my-project
bash /mnt/skills/user/typescript-master/scripts/type-check.sh ./my-project false
```

**Checks:**
- TypeScript compilation (noEmit)
- Strict type checking
- Unused variables/imports
- tsconfig recommendations

## Documentation Resources

**Official Documentation:**
- TypeScript Handbook: `https://www.typescriptlang.org/docs/handbook/`
- Type Challenges: `https://github.com/type-challenges/type-challenges`

## Type System Fundamentals

### Utility Types

```typescript
// Built-in utilities
type Partial<T> = { [P in keyof T]?: T[P] };
type Required<T> = { [P in keyof T]-?: T[P] };
type Readonly<T> = { readonly [P in keyof T]: T[P] };
type Pick<T, K extends keyof T> = { [P in K]: T[P] };
type Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>;
type Record<K extends keyof any, T> = { [P in K]: T };
```

### Custom Utility Types

```typescript
// Deep Partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Strict Omit (only known keys)
type StrictOmit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

// Make specific keys required
type RequireKeys<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Nullable
type Nullable<T> = T | null;
```

## Generics Patterns

### Constrained Generics

```typescript
// Key constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Type constraint
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}
```

### Inference with infer

```typescript
// Extract return type
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// Extract promise value
type Awaited<T> = T extends Promise<infer U> ? Awaited<U> : T;

// Extract array element
type ArrayElement<T> = T extends (infer E)[] ? E : never;

// Extract function parameters
type Parameters<T> = T extends (...args: infer P) => any ? P : never;
```

## Conditional Types

### Basic Conditional

```typescript
type IsString<T> = T extends string ? true : false;
type IsArray<T> = T extends any[] ? true : false;
```

### Distributive Conditional

```typescript
// Distributes over union
type ToArray<T> = T extends any ? T[] : never;
type Result = ToArray<string | number>; // string[] | number[]

// Prevent distribution
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;
type Result2 = ToArrayNonDist<string | number>; // (string | number)[]
```

## Discriminated Unions

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function handleResult<T>(result: Result<T>): T | null {
  if (result.success) {
    return result.data; // TypeScript knows data exists
  } else {
    console.error(result.error); // TypeScript knows error exists
    return null;
  }
}
```

## Type Guards

```typescript
// Custom type guard
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    typeof (obj as User).id === 'string'
  );
}

// Assertion function
function assertNonNull<T>(
  value: T,
  message?: string
): asserts value is NonNullable<T> {
  if (value === null || value === undefined) {
    throw new Error(message ?? 'Value is null or undefined');
  }
}
```

## Template Literal Types

```typescript
type EventName = 'click' | 'focus' | 'blur';
type Handler = `on${Capitalize<EventName>}`;
// "onClick" | "onFocus" | "onBlur"

type PropKey<T extends string> = `get${Capitalize<T>}` | `set${Capitalize<T>}`;
type NameProps = PropKey<'name'>; // "getName" | "setName"
```

## Recommended tsconfig

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": true,
    "moduleResolution": "bundler",
    "verbatimModuleSyntax": true
  }
}
```

## Present Results to User

When providing TypeScript solutions:
- Prefer type inference over explicit annotations
- Use `unknown` instead of `any`
- Leverage discriminated unions
- Provide type test examples
- Note TypeScript version features (5.0+: const type parameters)

## Troubleshooting

**"Type 'X' is not assignable to type 'Y'"**
- Check for missing properties
- Verify nullability handling
- Look for literal vs widened types

**"Property does not exist on type"**
- Add type guard before access
- Check if property is optional
- Verify union type narrowing

**"Excessive type complexity"**
- Break into smaller types
- Use intermediate type aliases
- Consider simplifying generics
